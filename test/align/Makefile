BASE=demo
DELIM=,
.SUFFIXES:

.PHONY : renamed raw zerofilled words features rawmphonemes clean

renamed : $(BASE)-renamed.pstr

raw : $(BASE)-raw.csv

zerofilled : $(BASE)-zerofilled.csv

words : $(BASE)-words.csv

features : $(BASE)-features.text

rawmphonemes : $(BASE)-rawmphonemes.text

compile :
	twol-comp $(BASE)-examples.pstr -t 2 $(BASE)-rules.twol

clean :
	rm -f $(BASE)-renamed.pstr $(BASE)-raw.csv
	rm -f $(BASE)-zerofilled.csv $(BASE)-words.csv
	rm -f $(BASE)-features.text $(BASE)-rawmphonemes.text

$(BASE)-renamed.pstr : $(BASE)-raw.csv $(BASE)-newnames.csv
	twol-raw2named.py $< $@ $(BASE)-newnames.csv

$(BASE)-raw.csv : $(BASE)-zerofilled.csv $(BASE)-affixes.csv
	twol-zerofilled2raw.py -d '$(DELIM)' $< $@ $(BASE)-affixes.csv

$(BASE)-zerofilled.csv : $(BASE)-words.csv
	twol-words2zerofilled.py alphabet.text -d '$(DELIM)' $< $@

$(BASE)-words.csv : $(BASE)-table.csv
	twol-table2words.py -d '$(DELIM)' -s "."  $< $@

$(BASE)-features.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | \
	tr ' ' '\n' | sort | uniq > $@

$(BASE)-rawmphonemes.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | \
	sort | egrep '^\{.+\}' | uniq > $@
