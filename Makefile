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

.PHONY: test
test:
	@if [[ $(OSTYPE) == "linux-gnu" ]] || [[ "$(OSTYPE)" == "darwin" ]]; then	\
		truncate testfs -s 1M;													\
		mkfs.vfat -F12 -S512 testfs;											\
		mkdir testmount;														\
		sudo mount -o loop,user,umask=000 testfs testmount/;					\
		cp tests/assets/info_uf2.txt testmount/;								\
	elif [[ "$(OSTYPE)" == "win32" ]]; then										\
		mkdir testmount;														\
		subst T: testmount;														\
	else																		\
		echo "Testing not supported on this platform";							\
		exit 1;																	\
	fi
	coverage run -m pytest
	coverage report
	coverage html
	@if [[ "$(OSTYPE)" == "linux-gnu" ]] || [[ "$(OSTYPE)" == "darwin" ]]; then	\
		sudo umount testmount;													\
		sudo rm -rf testmount;													\
		rm testfs;																\
	elif [[ "$(OSTYPE)" == "win32" ]]; then										\
		subst testmount /d;														\
		rmdir testmount /s;														\
	else																		\
		echo "Testing not supported on this platform";							\
		exit 1;																	\
	fi
