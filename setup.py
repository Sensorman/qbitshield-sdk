from pathlib import Path
import sys
import os

from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


ROOT = Path(__file__).parent
readme = (ROOT / "README.md").read_text(encoding="utf-8")

# Print banner when setup.py is executed (works with PEP 517 builds)
QBITSHIELD_BANNER = """
 ██████╗ ██████╗ ██╗████████╗███████╗██╗  ██╗██╗███████╗██╗     ██████╗ 
██╔═══██╗██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗
██║   ██║██████╔╝██║   ██║   ███████╗███████║██║█████╗  ██║     ██║  ██║
██║▄▄ ██║██╔══██╗██║   ██║   ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║
╚██████╔╝██████╔╝██║   ██║   ███████║██║  ██║██║███████╗███████╗██████╔╝
 ╚══▀▀═╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 

                               Engineering Entropy. Securing the Future. 
                               version  2.3.0
"""

def _is_interactive():
    """Check if running in interactive mode (has TTY)."""
    try:
        return sys.stdout.isatty() and sys.stderr.isatty()
    except (AttributeError, OSError):
        return False

def _print_banner():
    """Print the QbitShield banner."""
    try:
        print(QBITSHIELD_BANNER, file=sys.stderr, flush=True)
    except (AttributeError, OSError):
        # Fallback to stdout if stderr fails
        try:
            print(QBITSHIELD_BANNER, flush=True)
        except:
            pass

# Print banner at module load time - this runs even with PEP 517 builds
# when setuptools.build_meta imports setup.py during "Preparing editable metadata"
# Note: pip may suppress this output, but it will show when running setup.py directly
if os.getenv("_QBITSHIELD_SDK_BANNER_SHOWN") is None:
    try:
        # Always try to print (pip may suppress, but setup.py direct calls will show it)
        _print_banner()
        os.environ["_QBITSHIELD_SDK_BANNER_SHOWN"] = "1"
    except:
        pass


class QbitShieldBannerMixin:
    """Mixin class for banner display functionality."""
    
    def _is_interactive(self):
        """Check if running in interactive mode (has TTY)."""
        return _is_interactive()
    
    def _print_banner(self):
        """Print the QbitShield banner."""
        _print_banner()
    
    def _print_success(self):
        """Print success message after installation."""
        try:
            # Use print() which is more reliable
            print("\n" + "=" * 70, file=sys.stderr, flush=True)
            print("✅ QbitShield SDK installed successfully!", file=sys.stderr, flush=True)
            print("=" * 70, file=sys.stderr, flush=True)
            print("\n📚 Quick Start:", file=sys.stderr, flush=True)
            print("   from qbitshield.client import QbitShieldClient", file=sys.stderr, flush=True)
            print("   client = QbitShieldClient(base_url='...', api_key='...')", file=sys.stderr, flush=True)
            print("\n📖 Documentation:", file=sys.stderr, flush=True)
            print("   https://github.com/Sensorman/qbitshield-v2/tree/main/qbitshield-sdk", file=sys.stderr, flush=True)
            print("   See USER_GUIDE.md for comprehensive documentation", file=sys.stderr, flush=True)
            print("\n🚀 Get started: https://qbitshield-enterprise.vercel.app", file=sys.stderr, flush=True)
            print("=" * 70 + "\n", file=sys.stderr, flush=True)
        except:
            # Fallback to stdout
            try:
                print("\n" + "=" * 70, flush=True)
                print("✅ QbitShield SDK installed successfully!", flush=True)
                print("=" * 70 + "\n", flush=True)
            except:
                pass


class QbitShieldInstallCommand(QbitShieldBannerMixin, install):
    """Custom install command that displays a banner during installation."""
    
    def run(self):
        """Run the installation with banner display."""
        # Always show banner (pip might suppress it, but we try)
        self._print_banner()
        
        # Run the standard installation
        install.run(self)
        
        # Show success message
        self._print_success()


class QbitShieldDevelopCommand(QbitShieldBannerMixin, develop):
    """Custom develop command that displays a banner during editable installation."""
    
    def run(self):
        """Run the editable installation with banner display."""
        # Always show banner (pip might suppress it, but we try)
        self._print_banner()
        
        # Run the standard develop installation
        develop.run(self)
        
        # Show success message
        self._print_success()


class QbitShieldEggInfoCommand(QbitShieldBannerMixin, egg_info):
    """Custom egg_info command that displays banner early in the build process."""
    
    def run(self):
        """Run egg_info with banner display."""
        # Print banner early - this runs during PEP 517 builds
        self._print_banner()
        # Run standard egg_info
        egg_info.run(self)


setup(
    name="qbitshield",
    version="2.3.0",
    description="QbitShield Python SDK — quantum-safe key distribution via Prime Harmonic Modulation",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="QbitShield",
    author_email="support@qbitshield.com",
    url="https://github.com/Sensorman/qbitshield-v2",
    project_urls={
        "Documentation": "https://qbitshield-enterprise.vercel.app/documentation",
        "API Reference":  "https://qbitshield-api.railway.app/docs",
        "Issue Tracker":  "https://github.com/Sensorman/qbitshield-v2/issues",
    },
    license="MIT",
    packages=find_packages(include=["qbitshield", "qbitshield.*"]),
    python_requires=">=3.9",
    install_requires=[
        "cryptography>=42.0.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="quantum cryptography key-distribution post-quantum security nist prime-harmonics",
    cmdclass={
        "install": QbitShieldInstallCommand,
        "develop": QbitShieldDevelopCommand,
        "egg_info": QbitShieldEggInfoCommand,
    },
)
