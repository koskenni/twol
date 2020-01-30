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

examples : $(BASE)-examples.fst

compile :
	python3 ../twol.py $(BASE)-examples.fst -t 2 $(BASE)-rules.twol

clean :
	rm -f $(BASE)-renamed.pstr $(BASE)-raw.csv $(BASE)-zerofilled.csv $(BASE)-words.csv
	rm -f $(BASE)-features.text $(BASE)-rawmphonemes.text

$(BASE)-renamed.pstr : $(BASE)-raw.csv $(BASE)-newnames.csv
	python3 ../raw2named.py $< $@ $(BASE)-newnames.csv

$(BASE)-raw.csv : $(BASE)-zerofilled.csv $(BASE)-affixes.csv
	python3 ../zerofilled2raw.py -d '$(DELIM)' $< $@ $(BASE)-affixes.csv

$(BASE)-zerofilled.csv : $(BASE)-words.csv
	python3 ../words2zerofilled.py -d '$(DELIM)' $< $@

$(BASE)-words.csv : $(BASE)-table.csv
	python3 ../table2words.py -d '$(DELIM)' -s "."  $< $@

$(BASE)-features.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq > $@

$(BASE)-rawmphonemes.text : $(BASE)-raw.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '^\{.+\}' | uniq > $@

$(BASE)-examples.fst : $(BASE)-renamed.pstr
	python3 ../twexamp.py $< $@

#$(BASE)-rules.fst : $(BASE)-rules.twol $(BASE)-examples.fst
#	python3 ../twol.py $(BASE)-examples.fst $< -o $@
