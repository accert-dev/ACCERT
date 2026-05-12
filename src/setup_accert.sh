#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No color

# 1) Gather workbench_path from workbench.sh
workbench_path=$(grep "workbench_path" workbench.sh | cut -d '=' -f 2 | tr -d '"')

# 2) Check that workbench_path was retrieved
if [ -z "$workbench_path" ]; then
  echo -e "${RED}Error: workbench_path not found in workbench.sh${NC}"
  exit 1
else
  echo -e "${GREEN}workbench_path retrieved: $workbench_path${NC}"
fi

# 3) Check that retrieved path has subfolders
if [ ! -d "$workbench_path" ]; then
  echo -e "${RED}Error: workbench_path is not a valid directory${NC}"
  exit 1
else
  echo -e "${GREEN}workbench_path is a valid directory${NC}"
fi

# 4) Find conda
conda_path="${workbench_path}/rte/conda"
if [ ! -d "$conda_path" ]; then
  echo -e "${RED}Error: conda directory not found in workbench_path${NC}"
  exit 1
else
  echo -e "${GREEN}conda directory found: $conda_path${NC}"
fi


# 5) Set ACCERT_DIR to current directory
ACCERT_DIR=$(pwd)
echo -e "${GREEN}ACCERT_DIR set to: $ACCERT_DIR${NC}"

# 6) Use the pip in conda/bin to install requirements.txt located in the parent folder of this shell script
echo -e "${GREEN}Installing requirements from $ACCERT_DIR/../requirements.txt...${NC}"
if [ -x "$conda_path/bin/pip" ]; then
  "$conda_path/bin/pip" install -r "$ACCERT_DIR/../requirements.txt"
elif [ -x "$conda_path/Scripts/pip" ]; then
  "$conda_path/Scripts/pip" install -r "$ACCERT_DIR/../requirements.txt"
else
  echo -e "${RED}Error: pip executable not found in conda directory${NC}"
fi

echo -e "${GREEN}Installing requirements from $ACCERT_DIR/../requirements.txt using system pip...${NC}"
pip install -r "$ACCERT_DIR/../requirements.txt"

# 7) Install or refresh the bundled SQLite database.
echo -e "${GREEN}Installing SQLite database...${NC}"
if [ -x "$conda_path/bin/python" ]; then
  "$conda_path/bin/python" database_install.py
elif [ -x "$conda_path/Scripts/python" ]; then
  "$conda_path/Scripts/python" database_install.py
else
  python database_install.py
fi

# 8) cd into the parent folder of ACCERT_DIR
cd "$(dirname "$ACCERT_DIR")"
chmod 777 src/Main.py

# 9) Create symbolic link into ACCERT
echo -e "${GREEN}Creating symbolic links...${NC}"
# Copy accert_wb.py to rte/accert.py
cp src/etc/accert_wb.py "${workbench_path}/rte/accert.py"
# Check if bin directory exists, if not create it
if [ -d "$ACCERT_DIR/../bin" ]; then
  rm -r "$ACCERT_DIR/../bin"
fi
mkdir "$ACCERT_DIR/../bin"

ln -sf "${workbench_path}/bin/sonvalidxml" "$ACCERT_DIR/../bin/sonvalidxml"


# 10) Confirm installation is finished
echo -e "${GREEN}ACCERT has been set up.${NC}"
echo -e "${YELLOW}ACCERT uses the bundled SQLite database in src/accertdb.sqlite.${NC}"
