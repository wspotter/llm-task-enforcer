#!/bin/bash
# SuperManUS TaskEnforcer Installation Script
# One-command installation for any project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SUPERMANUS_REPO="https://github.com/wspotter/llm-task-enforcer.git"
TEMP_DIR="/tmp/supermanus-install-$$"
DEFAULT_TARGET_DIR="."

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🛡️  SuperManUS TaskEnforcer Installation"
    echo "========================================"
    echo -e "${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check for required commands
    local missing_commands=()
    
    if ! command -v python3 &> /dev/null; then
        missing_commands+=("python3")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_commands+=("git")
    fi
    
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        missing_commands+=("curl or wget")
    fi
    
    if [ ${#missing_commands[@]} -gt 0 ]; then
        print_error "Missing required commands: ${missing_commands[*]}"
        print_info "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to detect target directory
detect_target_directory() {
    if [ $# -eq 0 ]; then
        TARGET_DIR="$DEFAULT_TARGET_DIR"
    else
        TARGET_DIR="$1"
    fi
    
    # Convert to absolute path
    TARGET_DIR=$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")
    
    print_info "Target directory: $TARGET_DIR"
    
    # Check if directory exists and is writable
    if [ ! -d "$TARGET_DIR" ]; then
        print_error "Target directory does not exist: $TARGET_DIR"
        exit 1
    fi
    
    if [ ! -w "$TARGET_DIR" ]; then
        print_error "Target directory is not writable: $TARGET_DIR"
        exit 1
    fi
}

# Function to clone or download SuperManUS
download_supermanus() {
    print_info "Downloading SuperManUS TaskEnforcer..."
    
    # Clean up any existing temp directory
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    
    # Clone the repository
    if git clone "$SUPERMANUS_REPO" "$TEMP_DIR" &>/dev/null; then
        print_success "SuperManUS repository cloned successfully"
    else
        print_error "Failed to clone SuperManUS repository"
        print_info "Please check your internet connection and try again"
        exit 1
    fi
}

# Function to install core files
install_core_files() {
    print_info "Installing core SuperManUS files..."
    
    local supermanus_dir="$TARGET_DIR/supermanus"
    mkdir -p "$supermanus_dir"
    
    # Core Python files
    local core_files=(
        "task_enforcer.py"
        "llm_guard.py"
        "demo_enforcement.py"
    )
    
    for file in "${core_files[@]}"; do
        if [ -f "$TEMP_DIR/$file" ]; then
            cp "$TEMP_DIR/$file" "$supermanus_dir/"
            print_success "Installed $file"
        else
            print_warning "Core file not found: $file"
        fi
    done
    
    # Integrations directory
    if [ -d "$TEMP_DIR/integrations" ]; then
        cp -r "$TEMP_DIR/integrations" "$supermanus_dir/"
        print_success "Installed integrations directory"
    else
        print_warning "Integrations directory not found"
    fi
    
    # Make Python files executable
    chmod +x "$supermanus_dir"/*.py 2>/dev/null || true
}

# Function to install templates and documentation
install_templates() {
    print_info "Installing templates and documentation..."
    
    # Template files
    local template_files=(
        "SESSION_STATE.json"
        "WORK_LOG_TEMPLATE.md"
        "HUMAN_VALIDATION_GUIDE.md"
        "INTEGRATION_GUIDE.md"
    )
    
    for file in "${template_files[@]}"; do
        if [ -f "$TEMP_DIR/$file" ]; then
            # Don't overwrite existing files
            if [ ! -f "$TARGET_DIR/$file" ]; then
                cp "$TEMP_DIR/$file" "$TARGET_DIR/"
                print_success "Installed template: $file"
            else
                print_warning "Template already exists: $file (skipping)"
            fi
        fi
    done
    
    # Documentation directory
    if [ -d "$TEMP_DIR/docs" ]; then
        if [ ! -d "$TARGET_DIR/docs" ]; then
            cp -r "$TEMP_DIR/docs" "$TARGET_DIR/"
            print_success "Installed documentation directory"
        else
            print_warning "Documentation directory already exists (skipping)"
        fi
    fi
}

# Function to create project structure
create_project_structure() {
    print_info "Creating project structure..."
    
    local directories=(
        "work_logs"
        ".supermanus"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$TARGET_DIR/$dir"
        print_success "Created directory: $dir"
    done
    
    # Create default configuration
    local config_file="$TARGET_DIR/.supermanus/config.json"
    if [ ! -f "$config_file" ]; then
        cat > "$config_file" << 'EOF'
{
  "enforcement_level": "strict",
  "work_log_required": true,
  "auto_approve_patterns": [
    "documentation",
    "test_.*"
  ],
  "human_review_patterns": [
    "security_.*",
    "deploy_.*"
  ],
  "validation_timeout": 300,
  "integrations": {
    "cursor": {
      "enabled": true,
      "inject_context": true
    },
    "copilot": {
      "enabled": true,
      "context_length": 500
    },
    "claude_code": {
      "enabled": true,
      "require_justification": true
    }
  }
}
EOF
        print_success "Created default configuration"
    else
        print_warning "Configuration file already exists (skipping)"
    fi
}

# Function to customize SESSION_STATE.json
customize_session_state() {
    local session_file="$TARGET_DIR/SESSION_STATE.json"
    
    if [ -f "$session_file" ]; then
        print_info "Customizing SESSION_STATE.json..."
        
        # Get project name from directory
        local project_name=$(basename "$TARGET_DIR")
        local session_id=$(date +"%Y%m%d_%H%M%S")
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        # Use sed to customize the session state
        sed -i.bak \
            -e "s/\"current_session_id\": \".*\"/\"current_session_id\": \"${session_id}\"/" \
            -e "s/\"last_updated\": \".*\"/\"last_updated\": \"${timestamp}\"/" \
            -e "s/\"project_name\": \".*\"/\"project_name\": \"${project_name}\"/" \
            "$session_file" 2>/dev/null || {
            # Fallback for systems without GNU sed
            python3 -c "
import json
import sys
from datetime import datetime

try:
    with open('$session_file', 'r') as f:
        data = json.load(f)
    
    data['current_session_id'] = '$session_id'
    data['last_updated'] = '$timestamp'
    data['project_name'] = '$project_name'
    
    with open('$session_file', 'w') as f:
        json.dump(data, f, indent=2)
    print('Session state customized')
except Exception as e:
    print(f'Warning: Could not customize session state: {e}', file=sys.stderr)
" 2>/dev/null || true
        }
        
        # Remove backup file
        rm -f "${session_file}.bak" 2>/dev/null || true
        
        print_success "SESSION_STATE.json customized for project"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Check if requirements.txt exists in the downloaded repo
    if [ -f "$TEMP_DIR/requirements.txt" ]; then
        if python3 -m pip install -r "$TEMP_DIR/requirements.txt" --quiet; then
            print_success "Python dependencies installed"
        else
            print_warning "Some dependencies may not have installed correctly"
        fi
    elif [ -f "$TEMP_DIR/pyproject.toml" ]; then
        if python3 -m pip install -e "$TEMP_DIR" --quiet; then
            print_success "SuperManUS installed as Python package"
        else
            print_warning "Package installation may not have completed correctly"
        fi
    else
        print_info "No dependency file found, skipping Python dependencies"
    fi
}

# Function to run validation
run_validation() {
    print_info "Validating installation..."
    
    # Test Python imports
    if python3 -c "
import sys
sys.path.insert(0, '$TARGET_DIR/supermanus')
try:
    from task_enforcer import TaskSystemEnforcer
    from llm_guard import LLMGuard
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_success "Core module validation passed"
    else
        print_warning "Core module validation failed - check Python path"
    fi
    
    # Check file structure
    local required_files=(
        "supermanus/task_enforcer.py"
        "supermanus/llm_guard.py"
        "SESSION_STATE.json"
        "WORK_LOG_TEMPLATE.md"
        ".supermanus/config.json"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$TARGET_DIR/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "File structure validation passed"
    else
        print_warning "Some files missing: ${missing_files[*]}"
    fi
}

# Function to setup integrations
setup_integrations() {
    print_info "Setting up AI tool integrations..."
    
    # Setup Cursor integration if possible
    if python3 -c "
import sys
sys.path.insert(0, '$TARGET_DIR/supermanus')
try:
    from integrations.cursor_integration import setup_cursor_enforcement
    setup_cursor_enforcement()
    print('✅ Cursor integration configured')
except Exception as e:
    print('⚠️  Cursor integration setup failed')
" 2>/dev/null; then
        print_success "Cursor integration configured"
    fi
    
    # Setup Copilot integration if possible  
    if python3 -c "
import sys
sys.path.insert(0, '$TARGET_DIR/supermanus')
try:
    from integrations.github_copilot_integration import setup_copilot_enforcement
    setup_copilot_enforcement()
    print('✅ Copilot integration configured')
except Exception as e:
    print('⚠️  Copilot integration setup failed')
" 2>/dev/null; then
        print_success "Copilot integration configured"
    fi
}

# Function to cleanup
cleanup() {
    print_info "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    print_success "Cleanup complete"
}

# Function to print installation summary
print_summary() {
    echo -e "${GREEN}"
    echo "🎉 SuperManUS TaskEnforcer Installation Complete!"
    echo "=============================================="
    echo -e "${NC}"
    echo
    echo "📍 Installation Location: $TARGET_DIR"
    echo "📁 Core Files: $TARGET_DIR/supermanus/"
    echo "⚙️  Configuration: $TARGET_DIR/.supermanus/config.json"
    echo "📝 Session State: $TARGET_DIR/SESSION_STATE.json"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Review and customize SESSION_STATE.json for your project"
    echo "2. Define your project tasks in the active_tasks array"
    echo "3. Start using enforced operations:"
    echo
    echo "   ${BLUE}# Example usage${NC}"
    echo "   python3 -c \""
    echo "   import sys"
    echo "   sys.path.insert(0, '$TARGET_DIR/supermanus')"
    echo "   from integrations.claude_code_integration import select_task, enforced_write"
    echo "   select_task('SETUP.1: Configure SuperManUS')"
    echo "   enforced_write('test.py', 'print(\\\"Hello SuperManUS\\\")', 'Testing setup')"
    echo "   \""
    echo
    echo -e "${GREEN}📚 Documentation: $TARGET_DIR/docs/${NC}"
    echo -e "${GREEN}🧪 Run demo: python3 $TARGET_DIR/supermanus/demo_enforcement.py${NC}"
    echo
}

# Main installation function
main() {
    print_header
    
    # Parse command line arguments
    local target_dir="$1"
    
    # Check if running with --help
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [target_directory]"
        echo
        echo "Install SuperManUS TaskEnforcer in the specified directory"
        echo "If no directory is specified, installs in current directory"
        echo
        echo "Options:"
        echo "  -h, --help    Show this help message"
        echo
        echo "Example:"
        echo "  $0 /path/to/my/project"
        echo "  curl -sSL https://raw.githubusercontent.com/wspotter/llm-task-enforcer/main/install.sh | bash -s -- /path/to/project"
        exit 0
    fi
    
    # Run installation steps
    check_prerequisites
    detect_target_directory "$target_dir"
    download_supermanus
    install_core_files
    install_templates
    create_project_structure
    customize_session_state
    install_dependencies
    setup_integrations
    run_validation
    cleanup
    print_summary
    
    print_success "Installation completed successfully! 🎉"
}

# Trap to ensure cleanup on script exit
trap cleanup EXIT

# Run main installation
main "$@"