# Find all .ayed files, including setup.ayed
AYED_FILES_ALL := $(wildcard *.ayed)

# Exclude setup.ayed from the list of files to be compiled
AYED_FILES := $(filter-out setup.ayed, $(AYED_FILES_ALL))


SETUP_STATE := setup.st

MOVIE_FILES := $(AYED_FILES:.ayed=.mp4)

all: $(MOVIE_FILES) $(INSERT_MOVIES)

$(SETUP_STATE): setup.ayed $(wildcard tomos_ui.toml)
	@echo "Building setup.ayed to $(SETUP_STATE)"
	@tomos setup.ayed --save-state=$(SETUP_STATE) --movie=setup.mp4 --cfg=FRAMES_PARENT_PATH="\"/tmp\""

%.mp4: %.ayed $(SETUP_STATE) $(wildcard tomos_ui.toml)
	@echo "Building $< to $@"
	@tomos $< --load-state=$(SETUP_STATE) --explicit-frames --movie=$@ --cfg=FPS=3 --cfg=FRAMES_PARENT_PATH="\"/tmp\""

clean:
	rm -rf output_tomos
	rm -f $(SETUP_STATE) $(MOVIE_FILES) setup.mp4