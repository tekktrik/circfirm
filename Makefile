# SPDX-FileCopyrightText: 2024 Alec Delaney
#
# SPDX-License-Identifier: MIT


.PHONY: lint
lint:
	pre-commit run ruff --all-files

.PHONY: format
format:
	pre-commit run ruff-format --all-files

.PHONY: check
check:
	pre-commit run --all-files

.PHONY: test
test:
# Test setup
ifeq ("$(OS)","Windows_NT")
	@mkdir testmount
	@xcopy tests\assets\info_uf2.txt testmount
	@subst T: testmount
else
	@truncate testfs -s 1M
	@mkfs.vfat -F12 -S512 testfs
	@mkdir testmount
	@sudo mount -o loop,user,umask=000 testfs testmount/
	@cp tests/assets/info_uf2.txt testmount/
endif

# Run tests
	@coverage run -m pytest
	@coverage report
	@coverage html

# Test cleanup
ifeq "$(OS)" "Windows_NT"
	@subst T: /d
	@python scripts/rmdir.py testmount
else
	@sudo umount testmount
	@sudo rm -rf testmount
	@rm testfs
endif
