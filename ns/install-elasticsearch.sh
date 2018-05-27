sudo apt-get update && apt-get upgrade -y && apt-get install openjdk-8-jdk curl

curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.tar.gz
tar -xvf elasticsearch-6.2.4.tar.gz
cd elasticsearch-6.2.4
mkdir config/hunspell config/hunspell/cs_CZ
cd config/hunspell/cs_CZ
curl -sL -o cs_CZ.aff https://github.com/pavoltravnik/elasticsearch-cz/raw/master/cs_CZ.aff
curl -sL -o cs_CZ.dic https://github.com/pavoltravnik/elasticsearch-cz/raw/master/cs_CZ.dic
cd ../../../bin
./elasticsearch-plugin install analysis-icu
./elasticsearch -p elasticsearch-pid -d
