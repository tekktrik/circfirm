# SPDX-FileCopyrightText: 2024 Alec Delaney
# SPDX-License-Identifier: MIT

CIRCFIRM_TEST_DRIVEFILE1 := $(shell python scripts/mount.py 0 0)
CIRCFIRM_TEST_DIRECTORY1 := $(shell python scripts/mount.py 0 1)

CIRCFIRM_TEST_DRIVEFILE2 := $(shell python scripts/mount.py 1 0)
CIRCFIRM_TEST_DIRECTORY2 := $(shell python scripts/mount.py 1 1)


.PHONY: lint
lint:
	@pre-commit run ruff --all-files

.PHONY: format
format:
	@pre-commit run ruff-format --all-files

.PHONY: check
check:
	@pre-commit run --all-files

.PHONY: docs
docs:
	@sphinx-build -E -W -b html docs docs/_build

.PHONY: prepare
prepare: check test docs

.PHONY: test-mount
test-mount:
ifeq "$(OS)" "Windows_NT"
	-@mkdir $(CIRCFIRM_TEST_DIRECTORY)
	-@subst $(CIRCFIRM_TEST_DRIVEFILE) $(CIRCFIRM_TEST_DIRECTORY)
else ifeq "$(shell uname -s)" "Linux"
	-@truncate $(CIRCFIRM_TEST_DRIVEFILE) -s 1M
	-@mkfs.vfat -F12 -S512 $(CIRCFIRM_TEST_DRIVEFILE)
	-@mkdir $(CIRCFIRM_TEST_DIRECTORY)
	-@sudo mount -o loop,user,umask=000 $(CIRCFIRM_TEST_DRIVEFILE) $(CIRCFIRM_TEST_DIRECTORY)/
else ifeq "$(shell uname -s)" "Darwin"
	-@hdiutil create -size 512m -volname $(CIRCFIRM_TEST_DIRECTORY) -fs FAT32 $(CIRCFIRM_TEST_DRIVEFILE)
	-@hdiutil attach $(CIRCFIRM_TEST_DRIVEFILE)
else
	@echo "Current OS not supported"
	@exit 1
endif

.PHONY: test-prep
test-prep:
	-@"${MAKE}" test-mount CIRCFIRM_TEST_DRIVEFILE="$(CIRCFIRM_TEST_DRIVEFILE1)" CIRCFIRM_TEST_DIRECTORY="$(CIRCFIRM_TEST_DIRECTORY1)"
	-@"${MAKE}" test-mount CIRCFIRM_TEST_DRIVEFILE="$(CIRCFIRM_TEST_DRIVEFILE2)" CIRCFIRM_TEST_DIRECTORY="$(CIRCFIRM_TEST_DIRECTORY2)"
	-@git clone https://github.com/adafruit/circuitpython tests/sandbox/circuitpython --depth 1

.PHONY: test-run
test-run:
	@coverage run -m pytest
	-@coverage report
	-@coverage html

.PHONY: test-unmount
test-unmount:
ifeq "$(OS)" "Windows_NT"
	-@subst $(CIRCFIRM_TEST_DRIVEFILE) /d
	-@python scripts\rmdir.py $(CIRCFIRM_TEST_DIRECTORY)
else ifeq "$(shell uname -s)" "Linux"
	-@sudo umount $(CIRCFIRM_TEST_DIRECTORY)
	-@sudo rm -rf $(CIRCFIRM_TEST_DIRECTORY)
	-@rm $(CIRCFIRM_TEST_DRIVEFILE) -f
else
	-@hdiutil detach /Volumes/$(CIRCFIRM_TEST_DIRECTORY)
	-@rm $(CIRCFIRM_TEST_DRIVEFILE) -f
endif

.PHONY: test-clean
test-clean:
	-@"${MAKE}" test-unmount CIRCFIRM_TEST_DRIVEFILE="$(CIRCFIRM_TEST_DRIVEFILE1)" CIRCFIRM_TEST_DIRECTORY="$(CIRCFIRM_TEST_DIRECTORY1)"
	-@"${MAKE}" test-unmount CIRCFIRM_TEST_DRIVEFILE="$(CIRCFIRM_TEST_DRIVEFILE2)" CIRCFIRM_TEST_DIRECTORY="$(CIRCFIRM_TEST_DIRECTORY2)"
ifeq "$(OS)" "Windows_NT"
	-@python scripts\rmdir.py tests\sandbox\circuitpython
else
	-@rm -rf tests/sandbox/circuitpython
endif

.PHONY: test
test:
	-@"${MAKE}" test-prep --no-print-directory
	-@"${MAKE}" test-run --no-print-directory
	-@"${MAKE}" test-clean --no-print-directory
