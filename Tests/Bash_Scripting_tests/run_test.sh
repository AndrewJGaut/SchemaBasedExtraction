# first, run the create articles file
nohup python3.5 -u CreateArticleFile.py largescale_test.txt largescale_test2.txt &

# now, simultaneously, run the createDataset thing
nohup python3.5 -u CreateDBPediaDatsetsMP.py &
