# SPDX-FileCopyrightText: 2024 Alec Delaney
#
# SPDX-License-Identifier: MIT

OSTYPE := $(shell echo $$OSTYPE)

.PHONY: lint
lint:
	pre-commit run ruff --all-files

.PHONY: format
format:
	pre-commit run ruff-format --all-files

.PHONY: check
check:
	pre-commit run --all-files

.PHONY: test-linux
test-linux:
	truncate testfs -s 1M
	mkfs.vfat -F12 -S512 testfs
	mkdir testmount
	sudo mount -o loop,user,umask=000 testfs testmount/
	cp tests/assets/info_uf2.txt testmount/
	coverage run -m pytest
	coverage report
	coverage html
	sudo umount testmount
	sudo rm -rf testmount
	rm testfs


.PHONY: test-windows
test-windows:
	mkdir testmount
	takeown /F testmount
	icacls testmount /grant administrators:F
	xcopy tests\assets\info_uf2.txt testmount
	subst T: testmount
	coverage run -m pytest
	coverage report
	coverage html
	subst T: /d
	rmdir testmount /s /q
