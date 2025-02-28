include .env

# Find all .ayed files, including setup.ayed
AYED_FILES_ALL := $(wildcard *.ayed)

# Exclude setup.ayed from the list of files to be compiled
AYED_ALL_FILES := $(filter-out setup.ayed, $(AYED_FILES_ALL))

# Exclude insert_at.ayed from the list of files to be compiled
AYED_FILES := $(filter-out insert_at.ayed, $(AYED_FILES_ALL))
AYED_FILES := $(filter-out remove_first_data.ayed, $(AYED_FILES))

SETUP_STATE := setup.st

TOMOS_CFG := --cfg=FRAMES_PARENT_PATH="\"/tmp\"" --no-final-state

MOVIE_FILES := $(AYED_FILES:.ayed=.mp4)

INSERT_MOVIES := insert_at_neg.mp4 insert_at_0.mp4 insert_at_2.mp4 insert_at_bottom.mp4 insert_at_beyond_length.mp4
REMOVE_MOVIES := remove_first_data_found.mp4 remove_first_data_not_found.mp4

LENGTH := 5

all: $(MOVIE_FILES) $(INSERT_MOVIES) $(REMOVE_MOVIES)

$(SETUP_STATE): setup.ayed $(wildcard tomos_ui.toml)
	@echo "Building setup.ayed to $(SETUP_STATE)"
	LINKED_LIST_LENGTH=$(LENGTH) tomos setup.ayed --save-state=$(SETUP_STATE) --movie=setup.mp4 ${TOMOS_CFG}

%.mp4: %.ayed $(SETUP_STATE) $(wildcard tomos_ui.toml)
	@echo "Building $< to $@"
	@tomos $< --load-state=$(SETUP_STATE) --movie=$@ ${TOMOS_CFG}

insert_at_%.mp4: insert_at.ayed $(SETUP_STATE) $(wildcard tomos_ui.toml)
	@echo "Building $@"
	POSITION=$(value $@) tomos insert_at.ayed --load-state=$(SETUP_STATE) --movie=$@ ${TOMOS_CFG}

remove_first_data_%.mp4: remove_first_data.ayed $(SETUP_STATE) $(wildcard tomos_ui.toml)
	@echo "Building $@ with TO_REMOVE: $(TO_REMOVE)"
	TO_REMOVE=$(value $@) tomos remove_first_data.ayed --load-state=$(SETUP_STATE) --movie=$@ ${TOMOS_CFG}

clean:
	rm -rf output_tomos
	rm -f $(SETUP_STATE) $(MOVIE_FILES) setup.mp4 insert_at*.mp4 $(REMOVE_MOVIES) $(INSERT_MOVIES)
