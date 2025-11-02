#!/usr/bin/env python3
"""
MCP Configuration Validator

Validates MCP configuration files untuk memastikan compliance dengan
MCP Protocol 2025-06-18 standard.
"""

import json
import yaml
import logging
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Backport for older Python
    except ImportError:
        tomllib = None
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPConfigValidator:
    """Validator untuk MCP configuration files"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def validate_mcp_json(self) -> bool:
        """Validate mcp.json file"""
        logger.info("🔍 Validating mcp.json...")
        
        mcp_json_path = self.base_dir / "mcp.json"
        if not mcp_json_path.exists():
            self.errors.append("❌ mcp.json file not found")
            return False
        
        try:
            with open(mcp_json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = [
                "mcpVersion", "name", "description", "version",
                "server", "capabilities", "tools", "transport"
            ]
            
            for field in required_fields:
                if field not in config:
                    self.errors.append(f"❌ Missing required field: {field}")
            
            # Validate MCP version
            if config.get("mcpVersion") != "2025-06-18":
                self.errors.append(f"❌ Invalid MCP version: {config.get('mcpVersion')}")
            
            # Validate server configuration
            server_config = config.get("server", {})
            server_required = ["command", "args"]
            for field in server_required:
                if field not in server_config:
                    self.errors.append(f"❌ Missing server field: {field}")
            
            # Validate capabilities
            capabilities = config.get("capabilities", {})
            if "tools" not in capabilities:
                self.errors.append("❌ Missing tools capability")
            
            # Validate tools
            tools = config.get("tools", [])
            if not isinstance(tools, list) or len(tools) == 0:
                self.errors.append("❌ No tools defined")
            
            for i, tool in enumerate(tools):
                if not isinstance(tool, dict):
                    self.errors.append(f"❌ Tool {i} is not an object")
                    continue
                    
                tool_required = ["name", "description", "inputSchema"]
                for field in tool_required:
                    if field not in tool:
                        self.errors.append(f"❌ Tool {i} missing field: {field}")
            
            # Validate transport
            transport = config.get("transport", {})
            transport_required = ["type", "host", "port", "endpoints"]
            for field in transport_required:
                if field not in transport:
                    self.errors.append(f"❌ Missing transport field: {field}")
            
            if len(self.errors) == 0:
                logger.info("✅ mcp.json validation passed")
                return True
            else:
                logger.error(f"❌ mcp.json validation failed with {len(self.errors)} errors")
                return False
                
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ Invalid JSON in mcp.json: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ Error validating mcp.json: {e}")
            return False
    
    def validate_package_json(self) -> bool:
        """Validate package.json file"""
        logger.info("🔍 Validating package.json...")
        
        package_json_path = self.base_dir / "package.json"
        if not package_json_path.exists():
            self.warnings.append("⚠️ package.json file not found (optional)")
            return True
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check recommended fields
            recommended_fields = [
                "name", "version", "description", "scripts", "keywords"
            ]
            
            for field in recommended_fields:
                if field not in config:
                    self.warnings.append(f"⚠️ Missing recommended field in package.json: {field}")
            
            # Check MCP section
            if "mcp" in config:
                mcp_config = config["mcp"]
                if "mcpVersion" not in mcp_config:
                    self.warnings.append("⚠️ Missing mcpVersion in package.json mcp section")
                elif mcp_config["mcpVersion"] != "2025-06-18":
                    self.errors.append(f"❌ Invalid MCP version in package.json: {mcp_config['mcpVersion']}")
            
            logger.info("✅ package.json validation passed")
            return True
            
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ Invalid JSON in package.json: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ Error validating package.json: {e}")
            return False
    
    def validate_pyproject_toml(self) -> bool:
        """Validate pyproject.toml file"""
        logger.info("🔍 Validating pyproject.toml...")
        
        pyproject_path = self.base_dir / "pyproject.toml"
        if not pyproject_path.exists():
            self.warnings.append("⚠️ pyproject.toml file not found (optional)")
            return True
        
        if tomllib is None:
            self.warnings.append("⚠️ tomllib not available - skipping pyproject.toml validation")
            return True
        
        try:
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
            
            # Check project section
            if "project" not in config:
                self.errors.append("❌ Missing [project] section in pyproject.toml")
                return False
            
            project = config["project"]
            project_required = ["name", "version", "description", "dependencies"]
            for field in project_required:
                if field not in project:
                    self.errors.append(f"❌ Missing project field in pyproject.toml: {field}")
            
            # Check MCP section
            if "tool" in config and "mcp" in config["tool"]:
                mcp_config = config["tool"]["mcp"]
                if "mcpVersion" not in mcp_config:
                    self.warnings.append("⚠️ Missing mcpVersion in pyproject.toml [tool.mcp] section")
                elif mcp_config["mcpVersion"] != "2025-06-18":
                    self.errors.append(f"❌ Invalid MCP version in pyproject.toml: {mcp_config['mcpVersion']}")
            
            logger.info("✅ pyproject.toml validation passed")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Error validating pyproject.toml: {e}")
            return False
    
    def validate_mcp_config_yaml(self) -> bool:
        """Validate mcp-config.yaml file"""
        logger.info("🔍 Validating mcp-config.yaml...")
        
        config_yaml_path = self.base_dir / "mcp-config.yaml"
        if not config_yaml_path.exists():
            self.warnings.append("⚠️ mcp-config.yaml file not found (optional)")
            return True
        
        try:
            with open(config_yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Check main sections
            required_sections = ["mcp", "server", "transport", "ocr", "pdf"]
            for section in required_sections:
                if section not in config:
                    self.errors.append(f"❌ Missing section in mcp-config.yaml: {section}")
            
            # Validate MCP version
            if "mcp" in config and "version" in config["mcp"]:
                if config["mcp"]["version"] != "2025-06-18":
                    self.errors.append(f"❌ Invalid MCP version in config: {config['mcp']['version']}")
            else:
                self.errors.append("❌ Missing MCP version in mcp-config.yaml")
            
            logger.info("✅ mcp-config.yaml validation passed")
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"❌ Invalid YAML in mcp-config.yaml: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ Error validating mcp-config.yaml: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Validate all configuration files"""
        logger.info("🎯 Starting MCP Configuration Validation")
        logger.info("="*60)
        
        results = []
        
        # Validate each configuration file
        results.append(("mcp.json", self.validate_mcp_json()))
        results.append(("package.json", self.validate_package_json()))
        results.append(("pyproject.toml", self.validate_pyproject_toml()))
        results.append(("mcp-config.yaml", self.validate_mcp_config_yaml()))
        
        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        logger.info("\n" + "="*60)
        logger.info("📊 Validation Results:")
        logger.info("="*60)
        
        for config_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {config_name}")
        
        logger.info(f"\n📈 Summary: {passed}/{total} configurations valid")
        
        # Show errors and warnings
        if self.errors:
            logger.error(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"  {error}")
        
        if self.warnings:
            logger.warning(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  {warning}")
        
        if len(self.errors) == 0:
            logger.info("\n🎉 All MCP configurations are valid!")
            logger.info("✅ Ready for MCP Protocol 2025-06-18 compliance")
            return True
        else:
            logger.error(f"\n💥 Configuration validation failed!")
            logger.error(f"Please fix {len(self.errors)} errors before proceeding")
            return False
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate detailed validation report"""
        return {
            "validation_status": len(self.errors) == 0,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "mcp_version": "2025-06-18",
            "validated_files": [
                "mcp.json",
                "package.json", 
                "pyproject.toml",
                "mcp-config.yaml"
            ]
        }

def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Configuration Validator")
    parser.add_argument("--dir", default=".", help="Directory containing config files")
    parser.add_argument("--report", help="Save detailed report to JSON file")
    
    args = parser.parse_args()
    
    validator = MCPConfigValidator(Path(args.dir))
    success = validator.validate_all()
    
    # Save report if requested
    if args.report:
        report = validator.generate_summary_report()
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"📄 Detailed report saved to: {args.report}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()