Controllers = ["SMC", "PID", "SMC_without_wind", "PID_without_wind"];
graph_folder = "graps";
xPoints = {};
yPoints = {};
zPoints = {};
ptime = {};

xPointsRef = {};
yPointsRef = {};
zPointsRef = {};
ptimeRef = {};

xvelPoints = {};
yvelPoints = {};
zvelPoints = {};
veltime = {};

xvelrefPoints = {};
yvelrefPoints = {};
zvelrefPoints = {};
velreftime = {};

xPointsRef_interpolated = {};
yPointsRef_interpolated = {};
zPointsRef_interpolated = {};

BAG = {};

for i = 1:length(Controllers)

    Controller = Controllers(i);
    
    BAG{i} = rosbag(sprintf("%s_test.bag", Controller));
    
    titulo = sprintf("teste com controlador %s", Controller);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % msgStructs = readMessages(BAG,'DataFormat','struct');
    
    topic_pos = select(BAG{i}, 'Topic', '/mavros/local_position/pose');
    topic_pos_ref = select(BAG{i}, 'Topic', '/reference_pos');
    topic_vel = select(BAG{i}, 'Topic', '/mavros/local_position/velocity_local');
    topic_ref_vel = select(BAG{i}, 'Topic', '/mavros/setpoint_velocity/cmd_vel');
    topic_fuz = select(BAG{i}, 'Topic', '/wpg/fuzzy_values');
    
    data_pos = readMessages(topic_pos,'DataFormat','struct');
    data_pos_ref = readMessages(topic_pos_ref,'DataFormat','struct');
    data_vel = readMessages(topic_vel,'DataFormat','struct');
    data_ref_vel = readMessages(topic_ref_vel,'DataFormat','struct');
    data_fuz = readMessages(topic_fuz,'DataFormat','struct');
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    xPoints{i} = cellfun(@(m) double(m.Pose.Position.X),data_pos);
    yPoints{i} = cellfun(@(m) double(m.Pose.Position.Y),data_pos);
    zPoints{i} = cellfun(@(m) double(m.Pose.Position.Z),data_pos);
    timeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_pos);
    timeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_pos);
    ptime{i} = (timeNsecPoints./1000000000 + timeSecPoints);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    xPointsRef{i} = cellfun(@(m) double(m.Pose.Position.X),data_pos_ref);
    yPointsRef{i} = cellfun(@(m) double(m.Pose.Position.Y),data_pos_ref);
    zPointsRef{i} = cellfun(@(m) double(m.Pose.Position.Z),data_pos_ref);
    timeNsecPointsRef = cellfun(@(m) double(m.Header.Stamp.Nsec),data_pos_ref);
    timeSecPointsRef = cellfun(@(m) double(m.Header.Stamp.Sec),data_pos_ref);
    ptimeRef{i} = (timeNsecPointsRef./1000000000 + timeSecPointsRef);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    xvelPoints{i} = cellfun(@(m) double(m.Twist.Linear.X),data_vel);
    yvelPoints{i} = cellfun(@(m) double(m.Twist.Linear.Y),data_vel);
    zvelPoints{i} = cellfun(@(m) double(m.Twist.Linear.Z),data_vel);
    veltimeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_vel);
    veltimeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_vel);
    veltime{i} = (veltimeNsecPoints./1000000000 + veltimeSecPoints);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    xvelrefPoints{i} = cellfun(@(m) double(m.Twist.Linear.X),data_ref_vel);
    yvelrefPoints{i} = cellfun(@(m) double(m.Twist.Linear.Y),data_ref_vel);
    zvelrefPoints{i} = cellfun(@(m) double(m.Twist.Linear.Z),data_ref_vel);
    velreftimeNsecPoints = cellfun(@(m) double(m.Header.Stamp.Nsec),data_ref_vel);
    velreftimeSecPoints = cellfun(@(m) double(m.Header.Stamp.Sec),data_ref_vel);
    velreftime{i} = (velreftimeNsecPoints./1000000000 + velreftimeSecPoints);

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    time = ptimeRef{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    sourceSize = size(xPointsRef{i});
    t = linspace(stime, ftime, sourceSize(1));
    
    time = ptime{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    targetSize = size(xPoints{i});
    ti = linspace(stime, ftime, targetSize(1));
    
    xPointsRef_interpolated{i} = interp1(t, xPointsRef{i}, ti)';

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    time = ptimeRef{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    sourceSize = size(yPointsRef{i});
    t = linspace(stime, ftime, sourceSize(1));
    
    time = ptime{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    targetSize = size(yPoints{i});
    ti = linspace(stime, ftime, targetSize(1));
    
    yPointsRef_interpolated{i} = interp1(t, yPointsRef{i}, ti)';

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    time = ptimeRef{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    sourceSize = size(zPointsRef{i});
    t = linspace(stime, ftime, sourceSize(1));
    
    time = ptime{i} - BAG{i}.StartTime;
    stime = time(1);
    ftime = time(end);
    targetSize = size(zPoints{i});
    ti = linspace(stime, ftime, targetSize(1));
    
    zPointsRef_interpolated{i} = interp1(t, zPointsRef{i}, ti)';
end

FigName = strcat("path_complete");
path_complete_fig = figure('Name', FigName, 'Position', get(0, 'Screensize'));
plot3(xPointsRef{1},yPointsRef{1},zPointsRef{1},'DisplayName', 'Desired movement');
hold on
plot3(xPoints{1},yPoints{1},zPoints{1},'DisplayName', 'Real movement SMC with wind');
plot3(xPoints{2},yPoints{2},zPoints{2},'DisplayName', 'Real movement PID with wind');
plot3(xPoints{3},yPoints{3},zPoints{3},'DisplayName', 'Real movement SMC without wind');
plot3(xPoints{4},yPoints{4},zPoints{4},'DisplayName', 'Real movement PID without wind');
title('Position tracker');
hold off;

xlabel('Absolute Position x[m]');
ylabel('Absolute Position Y[m]')
zlabel('Absolute Position Z[m]')
legend('Location', 'northeast');
set(path_complete_fig, 'PaperPositionMode', 'auto');
exportgraphics(flower_complete_fig, strcat(fullfile(graph_folder, FigName), ".png"), 'Resolution', 900);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

FigName = "all_fig";
all_fig = figure('Name', FigName, 'Position', get(0, 'Screensize'));
for axis = 1:3
    for path = 1:3
        subplot(3, 3, path + axis*3 - 3);
        hold off
        for controller = 1:length(Controllers)
            if axis == 1
                my_title='Position error on X' + " ";
                my_PointsRef_interpolated = xPointsRef_interpolated{controller};
                my_Points = xPoints{controller};
            elseif axis == 2
                my_title='Position error on Y' + " ";
                my_PointsRef_interpolated = yPointsRef_interpolated{controller};
                my_Points = yPoints{controller};
            elseif axis == 3
                my_title='Position error on Z' + " ";
                my_PointsRef_interpolated = zPointsRef_interpolated{controller};
                my_Points = zPoints{controller};
            end
            change_1 = find(abs(diff(xPointsRef_interpolated{controller} - xPoints{controller}))>0.1);
            change_2 = find(abs(diff(zPointsRef_interpolated{controller} - xPoints{controller}))>0.1);
            change_1_start = change_1(1)   -2;
            change_1_end   = change_1(end) +2;
            change_2_start = change_2(1)   -2;
            change_2_end   = change_2(end) +2;
            
            time = ptime{controller} - BAG{controller}.StartTime;
            points = my_Points - my_PointsRef_interpolated;
            idx1 = find(~isnan(points), 1);
            first_valid_time = time(idx1);
            if controller == 1
                display_name = 'SMC with wind';
            elseif controller == 2
                display_name = 'PID with wind';
            elseif controller == 3
                display_name = 'SMC without wind';
            elseif controller == 4
                display_name = 'PID without wind';
            end
            if path == 1
                path_mode = 'on takeoff';
                plot(time(1:change_1_start) - first_valid_time, my_PointsRef_interpolated(1:change_1_start) - my_Points(1:change_1_start),'DisplayName',display_name );
            elseif path == 2
                path_mode = 'on move';
                plot(time(change_1_end:change_2_start) - first_valid_time, my_PointsRef_interpolated(change_1_end:change_2_start) - my_Points(change_1_end:change_2_start),'DisplayName',display_name );
            elseif path == 3
                path_mode = 'on landing';
                plot(time(change_2_end:end) - first_valid_time, my_PointsRef_interpolated(change_2_end:end) - my_Points(change_2_end:end),'DisplayName',display_name );
            end
            title(my_title + path_mode);
            xlabel('Time[s]');
            ylabel('Distance Error[m]')
            legend
            hold on
        end
    end
end
set(all_fig, 'PaperPositionMode', 'auto');
exportgraphics(all_fig, strcat(fullfile(graph_folder, FigName), ".png"), 'Resolution', 900);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

FigName = "all_fig_derivative";
all_fig_derivative = figure('Name', FigName, 'Position', get(0, 'Screensize'));
for axis = 1:3
    for path = 1:3
        subplot(3, 3, path + axis*3 - 3);
        hold off
        for controller = 1:length(Controllers)
            if axis == 1
                my_title='Absolute derivative of position error on X' + " ";
                my_PointsRef_interpolated = xPointsRef_interpolated{controller};
                my_Points = xPoints{controller};
            elseif axis == 2
                my_title='Absolute derivative of position error on Y' + " ";
                my_PointsRef_interpolated = yPointsRef_interpolated{controller};
                my_Points = yPoints{controller};
            elseif axis == 3
                my_title='Absolute derivative of position error on Z' + " ";
                my_PointsRef_interpolated = zPointsRef_interpolated{controller};
                my_Points = zPoints{controller};
            end
            change_1 = find(abs(diff(xPointsRef_interpolated{controller} - xPoints{controller}))>0.1);
            change_2 = find(abs(diff(zPointsRef_interpolated{controller} - xPoints{controller}))>0.1);
            change_1_start = change_1(1)   -2;
            change_1_end   = change_1(end) +2;
            change_2_start = change_2(1)   -2;
            change_2_end   = change_2(end) +2;
            
            time = ptime{controller} - BAG{controller}.StartTime;
            points= my_Points - my_PointsRef_interpolated;
            idx1 = find(~isnan(points), 1);
            first_valid_time = time(idx1);

            py1 = my_PointsRef_interpolated - my_Points;
            px1 = time - first_valid_time;
            dy1=diff(py1)./diff(px1);

            if controller == 1
                display_name = 'SMC with wind';
            elseif controller == 2
                display_name = 'PID with wind';
            elseif controller == 3
                display_name = 'SMC without wind';
            elseif controller == 4
                display_name = 'PID without wind';
            end
            if path == 1
                path_mode = '- takeoff';
                plot(px1(1:change_1_start),abs(dy1(1:change_1_start)),'DisplayName',display_name);
            elseif path == 2
                path_mode = '- move';
                plot(px1(change_1_end:change_2_start),abs(dy1(change_1_end:change_2_start)),'DisplayName',display_name);
            elseif path == 3
                path_mode = '- landing';
                plot(px1(change_2_end:end-1),abs(dy1(change_2_end:end)),'DisplayName',display_name);
            end
            title(my_title + path_mode);
            xlabel('Time[s]');
            ylabel('Distance Error Derivative[m]')
            legend
            hold on
        end
    end
end
set(all_fig_derivative, 'PaperPositionMode', 'auto');
exportgraphics(all_fig_derivative, strcat(fullfile(graph_folder, FigName), ".png"), 'Resolution', 900);
