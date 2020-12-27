This program is a distributed distance vector routing(DVR) algorithm. It will return the DV table of each router at the end. It can also show the process of changes.

To use this program, you should have a text file which is the network topology with an adjacency matrix. The default value of text file is test.txt (We also have a test2.txt). You can check its format, this program just accept this format.

First, you need to go to your terminal/CMD, then use python to run this py file.

Type following command: py DVR.py

Then you will be asked to enter your file name. If you use our default tests, filename should be test.txt and test2.txt

The result will show you what happened in each round and finally will return the last DV for each router and tell us after how many times it will convergence.