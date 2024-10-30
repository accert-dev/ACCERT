#!/bin/bash

NC='\033[0m' # No color

# 1) Gather workbench_path from workbench.sh
workbench_path=$(grep "workbench_path" workbench.sh | cut -d '=' -f 2 | tr -d '"')

# 2) Set NECOST_DIR to current directory
NECOST_DIR=$(pwd)
echo -e "${GREEN}NECOST_DIR set to: $NECOST_DIR${NC}"


# 3) cd into the parent folder of NECOST_DIR
cd "$(dirname "$NECOST_DIR")"
chmod 777 src/necostmain.py

# 4) Create symbolic link into NECOST
echo -e "${GREEN}Creating symbolic links...${NC}"
# Copy necost_wb.py to rte/necost.py
cp src/etc/necost_wb.py "${workbench_path}/rte/necost.py"


# 5) Confirm installation is finished
echo -e "${GREEN}NECOST has been set up.${NC}"
