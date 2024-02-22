# SPDX-FileCopyrightText: 2024 Alec Delaney
#
# SPDX-License-Identifier: MIT


.PHONY: lint
lint:
	@pre-commit run ruff --all-files

.PHONY: format
format:
	@pre-commit run ruff-format --all-files

.PHONY: check
check:
	@pre-commit run --all-files

.PHONY: test
test:
# Test setup
ifeq "$(OS)" "Windows_NT"
	@mkdir testmount
	@xcopy tests\assets\info_uf2.txt testmount
	@subst T: testmount
else ifeq "$(shell uname -s)" "Linux"
	@truncate testfs -s 1M
	@mkfs.vfat -F12 -S512 testfs
	@mkdir testmount
	@sudo mount -o loop,user,umask=000 testfs testmount/
	@cp tests/assets/info_uf2.txt testmount/
else ifeq "$(shell uname -s)" "Darwin"
	@hdiutil create -size 512m -volname TESTMOUNT -fs FAT32 testfs.dmg
	@hdiutil attach testfs.dmg
	@cp tests/assets/info_uf2.txt /Volumes/TESTMOUNT
else
	@echo "Current OS not supported"
	@exit 1
endif

# Run tests
	@coverage run -m pytest
	@coverage report
	@coverage html

# Test cleanup
ifeq "$(OS)" "Windows_NT"
	@subst T: /d
	@python scripts/rmdir.py testmount
else ifeq "$(shell uname -s)" "Linux"
	@sudo umount testmount
	@sudo rm -rf testmount
	@rm testfs
else
	@hdiutil detach /Volumes/TESTMOUNT
	@rm testfs.dmg
endif
