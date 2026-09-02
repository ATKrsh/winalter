# WinAlter — Windows Image Engineering Platform

**WinAlter** is a Windows image engineering platform and visual IDE for building custom Windows distributions. Rather than treating customization as a set of isolated hacks or ISO repacking scripts, WinAlter introduces a **declarative build engine** that compiles a high-level distribution specification (`winalter.yaml`) into precise, risk-classified image servicing operations across offline WIM images, registry hives, DISM, and unattended setup files.

---

## Architectural Highlights

1. **Declarative Distribution Specification (`winalter.yaml`)**:
   - Every distribution is defined declaratively using the Windows Build Language schema.
2. **Concept-Based Abstraction Layer**:
   - UI and CLI interact with abstract concepts (`Appearance`, `Explorer`, `Taskbar`, `Services`, `Security`, `OOBE`).
   - Dedicated providers translate concepts into DISM package/driver/feature commands, offline HKLM registry edits (`SOFTWARE`, `SYSTEM`, `DEFAULT`, `NTUSER.DAT`), policies, and answer files.
3. **Risk Classification Engine**:
   - Every customization operation is evaluated with a risk rating (**Supported**: Low, **Configuration**: Medium, **Provisioning**: Medium, **Advanced**: High, **Binary**: Very High, **Kernel**: Extreme).
4. **Layered Execution AST**:
   - Compiles specifications into 5 distinct execution layers (`Core OS & Servicing` -> `Provisioning & Apps` -> `System Services` -> `Shell & Customization` -> `Setup & OOBE`).
5. **Dual User Interfaces**:
   - **WinAlter Visual OS Studio**: Visual IDE Web dashboard with live `winalter.yaml` editor, risk-assessed AST plan view, and real-time build streaming (`http://localhost:5100`).
   - **WinAlter CLI Compiler**: Command line tool for validating and compiling distributions (`python main.py build --iso C:\Win11.iso`).

---

## Quick Start

### 1. Launch WinAlter Visual OS Studio
```powershell
python main.py
```
*Opens browser to `http://localhost:5100` automatically.*

### 2. Validate Distribution Spec (CLI)
```powershell
python main.py validate sample_spec.yaml
```

### 3. Build Distribution (CLI)
```powershell
python main.py build sample_spec.yaml --iso C:\Path\To\Win11.iso
```

---

## Administrator Rights & Requirements
- Windows 10 / 11 Operating System
- Modifying offline WIM images via DISM and loading offline registry hives require Windows Administrator privileges. Run your prompt as Administrator.
