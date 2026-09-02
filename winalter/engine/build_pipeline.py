"""
Layered Build Engine Pipeline for WinAlter
Executes compiled execution plans layer-by-layer over mounted WIM workspace images.
"""

import os
import glob
import subprocess
import logging
from typing import Dict, List, Any, Optional, Callable

from ..core.config import WinAlterSpec
from ..core.ast_compiler import WinAlterCompiler, ExecutionPlan
from ..core.workspace import WorkspaceManager
from ..analyzer.iso_importer import ISOImporter
from ..providers.dism_provider import DISMProvider
from ..providers.registry import RegistryProvider
from ..providers.shell_provider import ShellProvider
from ..providers.service import ServiceProvider
from ..providers.oobe import OOBEProvider

logger = logging.getLogger("WinAlter.BuildEngine")

class WinAlterBuildEngine:
    def __init__(self, workspace_root: str = "project_workspace", output_dir: str = "dist"):
        self.workspace = WorkspaceManager(workspace_root)
        self.workspace.initialize_workspace()
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def get_versioned_iso_path(self, prefix: str = "WinAlter_Custom", extension: str = ".iso") -> str:
        existing = glob.glob(os.path.join(self.output_dir, f"{prefix}_v*{extension}"))
        max_ver = 0
        for f in existing:
            base = os.path.basename(f)
            ver_part = base.replace(prefix + "_v", "").replace(extension, "")
            if ver_part.isdigit():
                max_ver = max(max_ver, int(ver_part))
        return os.path.join(self.output_dir, f"{prefix}_v{max_ver + 1}{extension}")

    def execute_build(
        self,
        spec: WinAlterSpec,
        iso_path: str,
        edition_index: int = 1,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        def log(msg: str):
            logger.info(msg)
            if log_callback:
                log_callback(msg)

        log("==================================================")
        log("  WinAlter Windows Image Engineering Platform")
        log("==================================================")
        log(f"Distribution Spec: {spec.meta.name} (v{spec.meta.version})")
        log(f"Target Edition Index: {edition_index}")
        log(f"Source ISO: {iso_path}")

        # Step 1: Import ISO into workspace source directory
        log("\n[Phase 1] Importing ISO into project workspace...")
        importer = ISOImporter(self.workspace.source_dir)
        importer.import_iso(iso_path, progress_callback=log)
        wim_path = importer.find_install_wim()

        # Step 2: Compile Spec into AST Execution Plan
        log("\n[Phase 2] Compiling declarative specification into AST Execution Plan...")
        compiler = WinAlterCompiler(spec)
        plan = compiler.compile()
        log(f"Compiled {sum(len(nodes) for nodes in plan.layers.values())} operations across {len(plan.layers)} layers.")

        # Step 3: Mount WIM Image
        log(f"\n[Phase 3] Mounting WIM image index {edition_index} to {self.workspace.mount_dir}...")
        mount_cmd = ["dism", "/English", "/Mount-Wim", f"/WimFile:{wim_path}", f"/Index:{edition_index}", f"/MountDir:{self.workspace.mount_dir}"]
        p = subprocess.Popen(mount_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            if line.strip():
                log(line.strip())
        p.wait()
        if p.returncode != 0:
            raise RuntimeError(f"DISM Mount failed with code {p.returncode}")

        # Step 4: Execute AST Layers
        log("\n[Phase 4] Executing AST Layers...")
        providers = {
            "DISMProvider": DISMProvider(self.workspace.mount_dir),
            "RegistryProvider": RegistryProvider(self.workspace.mount_dir),
            "ShellProvider": ShellProvider(self.workspace.mount_dir),
            "ServiceProvider": ServiceProvider(self.workspace.mount_dir),
            "OOBEProvider": OOBEProvider(self.workspace.mount_dir)
        }

        for layer_name, nodes in plan.layers.items():
            log(f"\n>>> Executing {layer_name} ({len(nodes)} operations)...")
            for node in nodes:
                provider = providers.get(node.provider)
                if provider:
                    log(f"Executing operation: {node.provider}.{node.action} [{node.risk['level'].value}]")
                    provider.execute(node.action, node.params, progress_callback=log)

        # Step 5: Unmount WIM and Commit
        log("\n[Phase 5] Committing layer modifications and unmounting WIM...")
        unmount_cmd = ["dism", "/English", "/Unmount-Wim", f"/MountDir:{self.workspace.mount_dir}", "/Commit"]
        p = subprocess.Popen(unmount_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            if line.strip():
                log(line.strip())
        p.wait()
        if p.returncode != 0:
            raise RuntimeError(f"DISM Unmount failed with code {p.returncode}")

        # Step 6: Build Output Bootable ISO
        output_iso = self.get_versioned_iso_path()
        log(f"\n[Phase 6] Packaging customized distribution into bootable ISO: {output_iso}...")
        
        ps_build = f"""
        $source = '{self.workspace.source_dir}'
        $target = '{output_iso}'
        $image = New-Object -ComObject IMAPI2FS.MsftFileSystemImage
        $image.ChooseImageDefaultsForMediaType(12)
        $image.FileSystemsToCreate = 3
        $image.Root.AddTree($source, $false)
        $result = $image.CreateResultImage()
        $stream = $result.ImageStream
        $fileStream = [System.IO.File]::Create($target)
        $buffer = New-Object byte[] (64 * 1024)
        while (($bytesRead = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {{
            $fileStream.Write($buffer, 0, $bytesRead)
        }}
        $fileStream.Close()
        Write-Host "ISO created successfully."
        """
        p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_build], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            if line.strip():
                log(line.strip())
        p.wait()

        log("==================================================")
        log("  WinAlter Build Pipeline Completed Successfully!")
        log(f"  Final Distribution ISO: {output_iso}")
        log("==================================================")

        return output_iso
