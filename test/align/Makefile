BASE=demo
DELIM=,
ZEROS=0
.SUFFIXES:

.PHONY : renamed raw zerofilled words features rawmphonemes clean compare

renamed : $(BASE)-renamed.pstr

raw : $(BASE)-raw.csv

zerofilled : $(BASE)-zerofilled.csv

words : $(BASE)-words.csv

features : $(BASE)-features.text

rawmphonemes : $(BASE)-rawmphonemes.text

compile :
	twol-comp $(BASE)-examples.pstr -t 2 $(BASE)-rules.twol

$(BASE)-renamed.pstr : $(BASE)-raw.csv $(BASE)-newnames.csv
	twol-raw2named $< $@ $(BASE)-newnames.csv

$(BASE)-raw.csv : $(BASE)-zerofilled.csv $(BASE)-affixes.csv
	twol-zerofilled2raw -d '$(DELIM)' $< $@ $(BASE)-affixes.csv

$(BASE)-zerofilled.csv : $(BASE)-words.csv
	twol-words2zerofilled -x $(ZEROS) -d '$(DELIM)' $< $@ alphabet.text

$(BASE)-words.csv : $(BASE)-table.csv
	twol-table2words -d '$(DELIM)' -s "."  $< $@

$(BASE)-features.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | \
	tr ' ' '\n' | sort | uniq > $@

$(BASE)-rawmphonemes.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | \
	sort | egrep '^\{.+\}' | uniq > $@

clean :
	rm -f $(BASE)-renamed.pstr $(BASE)-raw.csv
	rm -f $(BASE)-zerofilled.csv $(BASE)-words.csv
	rm -f $(BASE)-features.text $(BASE)-rawmphonemes.text

compare :
	# ----------------------------------------
	diff $(BASE)-zerofilled-orig.csv $(BASE)-zerofilled.csv | head -20
	# ----------------------------------------
	diff $(BASE)-raw-orig.csv $(BASE)-raw.csv | head -20
	# ----------------------------------------
	diff $(BASE)-renamed-orig.pstr $(BASE)-renamed.pstr | head -20
