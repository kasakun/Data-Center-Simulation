import os

#os.mkdir('results')
for i in range(1,49):
	s = "sudo ./waf --run 'scratch/ICTCP_TEST --Activate_clients=%s'"%i
	os.system(s)
