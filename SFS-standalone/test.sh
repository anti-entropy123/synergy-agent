#!/bin/bash

# ./main -p c -t test2 -n 1 > /result/cfs.txt
# ./main -p f -t test2 -n 1 > /result/fifo.txt
#./main -p m -t test2 -n 1 > /result/sfs.txt
#./main -p s -t test1 -n 12 > ./result/srtf.txt

# ./main -p f -t heap-chameleon-1727/dp1.txt -n 1 > heapChameleonResult-1727/sfs_fifo_dp1.txt
# ./main -p f -t heap-chameleon-1727/dp2.txt -n 1 > heapChameleonResult-1727/sfs_fifo_dp2.txt
# ./main -p f -t heap-chameleon-1727/hash1.txt -n 1 > heapChameleonResult-1727/sfs_fifo_hash1.txt
# ./main -p f -t heap-chameleon-1727/hash2.txt -n 1 > heapChameleonResult-1727/sfs_fifo_hash2.txt
# ./main -p f -t heap-chameleon-1727/poll1.txt -n 1 > heapChameleonResult-1727/sfs_fifo_poll1.txt
# ./main -p f -t heap-chameleon-1727/poll2.txt -n 1 > heapChameleonResult-1727/sfs_fifo_poll2.txt
# ./main -p f -t heap-chameleon-1727/random1.txt -n 1 > heapChameleonResult-1727/sfs_fifo_random1.txt
# ./main -p f -t heap-chameleon-1727/random2.txt -n 1 > heapChameleonResult-1727/sfs_fifo_random2.txt

# ./main -p c -t heap-chameleon-1727/dp1.txt -n 1 > heapChameleonResult-1727/sfs_cfs_dp1.txt
# ./main -p c -t heap-chameleon-1727/dp2.txt -n 1 > heapChameleonResult-1727/sfs_cfs_dp2.txt
# ./main -p c -t heap-chameleon-1727/hash1.txt -n 1 > heapChameleonResult-1727/sfs_cfs_hash1.txt
# ./main -p c -t heap-chameleon-1727/hash2.txt -n 1 > heapChameleonResult-1727/sfs_cfs_hash2.txt
# ./main -p c -t heap-chameleon-1727/poll1.txt -n 1 > heapChameleonResult-1727/sfs_cfs_poll1.txt
# ./main -p c -t heap-chameleon-1727/poll2.txt -n 1 > heapChameleonResult-1727/sfs_cfs_poll2.txt
# ./main -p c -t heap-chameleon-1727/random1.txt -n 1 > heapChameleonResult-1727/sfs_cfs_random1.txt
# ./main -p c -t heap-chameleon-1727/random2.txt -n 1 > heapChameleonResult-1727/sfs_cfs_random2.txt

# ./main -p m -t heap-chameleon-1727/dp1.txt -n 1 > heapChameleonResult-1727/sfs_dp1.txt
# ./main -p m -t heap-chameleon-1727/dp2.txt -n 1 > heapChameleonResult-1727/sfs_dp2.txt
# ./main -p m -t heap-chameleon-1727/hash1.txt -n 1 > heapChameleonResult-1727/sfs_hash1.txt
# ./main -p m -t heap-chameleon-1727/hash2.txt -n 1 > heapChameleonResult-1727/sfs_hash2.txt
# ./main -p m -t heap-chameleon-1727/poll1.txt -n 1 > heapChameleonResult-1727/sfs_poll1.txt
# ./main -p m -t heap-chameleon-1727/poll2.txt -n 1 > heapChameleonResult-1727/sfs_poll2.txt
# ./main -p m -t heap-chameleon-1727/random1.txt -n 1 > heapChameleonResult-1727/sfs_random1.txt
# ./main -p m -t heap-chameleon-1727/random2.txt -n 1 > heapChameleonResult-1727/sfs_random2.txt

./main -p m -t not_modified_test1_fourth_column_data_to_0.txt -n 1 > test_SFS_test1_And_test2/test1_num.txt
./main -p m -t not_modified_test2_fourth_column_data_to_0.txt -n 1 > test_SFS_test1_And_test2/test2_num.txt

./main -p m -t 20240220-40.6-22.7-15.7-9.8-6.8/shuffled_output.txt -n 1 > 20240220-40.6-22.7-15.7-9.8-6.8/sfs.txt
./main -p m -t 34-35.txt -n 1 > 20240220-小中大请求/da_sfs.txt

./main -p m -t result/hash2.txt -n 1 > result/hash2_sfs.txt

./main -p m -t data-20240228/240313/20-26.txt -n 1 > data-20240228/240313/20-26_result.txt
./main -p m -t data-20240228/240315/3-20_2-29.txt -n 1 > data-20240228/240315/3-20_2-29_result.txt
./main -p c -t 123 -n 1 > data-20240228/240320/34-35_cfs.txt
htop
taskset -c 1 ./main -p c -t 123 -n 1 > data-20240228/240320/34-35_cfs.txt

./main -p m -t data/240422/hash1010.txt -n 1 > data/240422/result/hash1010_result.txt

./main -p f -t test3 -n 1 > data/240607-motivation/ob1/result-long-first/l-40-s-1-r-f.txt

./main -p f -t test3 -n 1 > data/240607-motivation/ob1/result-short-first/s-40-l-1-r-f.txt

./main -p f -t test3 -n 1 > data/240607-motivation/ob1/result-long-first/c-l-40-s-1-r.txt

./main -p c -t test3 -n 1 > data/240607-motivation/ob1/result-long-first/c-l-40-s-1-r.txt

./main -p c -t test3 -n 1 > data/240607-motivation/ob2/long-first-l-1-s-10-r.txt

./main -p f -t test3 -n 1 > data/240607-motivation/ob1-5/f-s-60-l-2-r.txt

./main -p c -t test3 -n 1 > data/240607-motivation/ob2-1/c-20-1300-r.txt

./main -p f -t test3 -n 1 > data/240607-motivation/ob3/f-1-long-r.txt