download-images:
	for i in $(shell seq 31); do \
        wget http://friends-shogi.com/images/avators/$$i.png -O images/$$i.png; \
    done
