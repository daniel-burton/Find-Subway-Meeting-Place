wget https://transitfeeds.com/p/mta/79/20181221/download;
mkdir data;
echo "Created \'Data\' Folder";
unzip download -d data; 
echo "Created 'Graph' Folder";
mkdir graph;
echo 'Now running python script to create graph...';
python3 process_data.py;
rm download;
