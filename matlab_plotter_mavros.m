%P = rosbag("P_4.bag");
%PD = rosbag("PD_3_0.08.bag");
%PI = rosbag("PI_3.2_0.95.bag");
%PID1 = rosbag("PID_2.60_0.25_0.40.bag");
BAG = rosbag('PID_test.bag');
%BAG = rosbag('DuzzyCorr.bag');


titulo = "teste com controlador PID";

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% msgStructs = readMessages(BAG,'DataFormat','struct');

topic_pos = select(BAG, 'Topic', '/mavros/local_position/pose');
topic_pos_ref = select(BAG, 'Topic', '/reference_pos');
topic_vel = select(BAG, 'Topic', '/mavros/local_position/velocity_local');
topic_ref_vel = select(BAG, 'Topic', '/mavros/setpoint_velocity/cmd_vel');
topic_fuz = select(BAG, 'Topic', '/wpg/fuzzy_values');

data_pos = readMessages(topic_pos,'DataFormat','struct');
data_pos_ref = readMessages(topic_pos_ref,'DataFormat','struct');
data_vel = readMessages(topic_vel,'DataFormat','struct');
data_ref_vel = readMessages(topic_ref_vel,'DataFormat','struct');
data_fuz = readMessages(topic_fuz,'DataFormat','struct');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xPoints = cellfun(@(m) double(m.Pose.Position.X),data_pos);
yPoints = cellfun(@(m) double(m.Pose.Position.Y),data_pos);
zPoints = cellfun(@(m) double(m.Pose.Position.Z),data_pos);
timeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_pos);
timeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_pos);
ptime = (timeNsecPoints./1000000000 + timeSecPoints);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xPointsRef = cellfun(@(m) double(m.Pose.Position.X),data_pos_ref);
yPointsRef = cellfun(@(m) double(m.Pose.Position.Y),data_pos_ref);
zPointsRef = cellfun(@(m) double(m.Pose.Position.Z),data_pos_ref);
timeNsecPointsRef = cellfun(@(m) double(m.Header.Stamp.Nsec),data_pos_ref);
timeSecPointsRef = cellfun(@(m) double(m.Header.Stamp.Sec),data_pos_ref);
ptimeRef = (timeNsecPointsRef./1000000000 + timeSecPointsRef);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xvelPoints = cellfun(@(m) double(m.Twist.Linear.X),data_vel);
yvelPoints = cellfun(@(m) double(m.Twist.Linear.Y),data_vel);
zvelPoints = cellfun(@(m) double(m.Twist.Linear.Z),data_vel);
veltimeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_vel);
veltimeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_vel);
veltime = (veltimeNsecPoints./1000000000 + veltimeSecPoints);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xvelrefPoints = cellfun(@(m) double(m.Twist.Linear.X),data_ref_vel);
yvelrefPoints = cellfun(@(m) double(m.Twist.Linear.Y),data_ref_vel);
zvelrefPoints = cellfun(@(m) double(m.Twist.Linear.Z),data_ref_vel);
velreftimeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_ref_vel);
velreftimeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_ref_vel);
velreftime = (velreftimeNsecPoints./1000000000 + velreftimeSecPoints);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
refxPoints = cellfun(@(m) double(m.Twist.Linear.X),data_ref_vel);
refyPoints = cellfun(@(m) double(m.Twist.Linear.Y),data_ref_vel);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2, 3, 1)
xlabel('x-axis')
xlim([0 inf]) 
plot(ptime - BAG.StartTime, xPoints,'DisplayName','X position');
hold on
plot(ptimeRef - BAG.StartTime, xPointsRef,'DisplayName','Y ref position');
title('Posição X')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2, 3, 2)
xlabel('y-axis')
xlim([0 inf]) 
plot(ptime - BAG.StartTime, yPoints,'DisplayName','Y position');
hold on
plot(ptimeRef - BAG.StartTime, yPointsRef,'DisplayName','Y ref position');
title('Posição Y')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2, 3, 3)
xlabel('z-axis')
xlim([0 inf]) 
plot(ptime - BAG.StartTime, zPoints,'DisplayName','Z position');
hold on
plot(ptimeRef - BAG.StartTime, zPointsRef,'DisplayName','Z ref position');
title('Posição Z')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

subplot(2, 3, 4)
plot(veltime - BAG.StartTime, xvelPoints,'DisplayName','X Velocity');
hold on
plot(velreftime - BAG.StartTime, xvelrefPoints,'DisplayName','X Velocity REF');
xlim([0 inf]) 
title('Xvel')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

subplot(2, 3, 5)
plot(veltime - BAG.StartTime, yvelPoints,'DisplayName','Y Velocity');
hold on
plot(velreftime - BAG.StartTime, yvelrefPoints,'DisplayName','Y Velocity REF');
xlim([0 inf]) 
title('Yvel')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

subplot(2, 3, 6)
plot(veltime - BAG.StartTime, zvelPoints,'DisplayName','Z Velocity');
hold on
plot(velreftime - BAG.StartTime, zvelrefPoints,'DisplayName','Z Velocity REF');
xlim([0 inf])
title('Zvel')
hold off
legend

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure
plot3(xPoints,yPoints,zPoints,'DisplayName', 'real movement')
hold on
plot3(xPointsRef,yPointsRef,zPointsRef,'DisplayName', 'wanted movement')
xlabel('X')
ylabel('Y')
zlabel('Z')
title('Position tracker')
hold off
legend