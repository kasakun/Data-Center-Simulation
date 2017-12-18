%% Author: Ruijia Wang

clear;
clc;
load('output_data.mat')

%% Goodput
f1 = figure();
hold on
plot(1:48, Tcpveno(:,2));
plot(1:48, ICTCP(:,2));
plot(1:48, Improved(:,2));
legend('Tcpveno','ICTCP','Improved')
title('Plot of Goodput')
xlabel('Number of clients')
ylabel('Goodput(Mbps)')
saveas(f1,'Goodput.jpg')

%% Loss Rate
f2 = figure();
hold on
plot(1:48, Tcpveno(:,3));
plot(1:48, ICTCP(:,3));
plot(1:48, Improved(:,3));
legend('Tcpveno','ICTCP','Improved')
title('Plot of Loss Rate')
xlabel('Number of clients')
ylabel('Loss Rate(%)')
saveas(f2,'LossRate.jpg')

%% Ratio of Tcp timeout
f3 = figure();
hold on
plot(1:48, Tcpveno(:,1));
plot(1:48, ICTCP(:,1));
plot(1:48, Improved(:,1));
legend('Tcpveno','ICTCP','Improved')
title('Ratio Tcp timeout')
xlabel('Number of clients')
ylabel('Ratio of Tcp timeout')
saveas(f3,'Timeout.jpg')

%% Throughput
f4 = figure();
hold on
plot(1:48, Tcpveno(:,4));
plot(1:48, ICTCP(:,4));
plot(1:48, Improved(:,4));
legend('Tcpveno','ICTCP','Improved')
title('Plot of Throughput')
xlabel('Number of clients')
ylabel('Throughput(Mbps)')
saveas(f4,'Throughput.jpg')



