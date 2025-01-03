function rosmsgOut = defuzzy_vel_modif(slBusIn, rosmsgOut)
%#codegen
%   Copyright 2021 The MathWorks, Inc.
    rosmsgOut.Header = bus_conv_fcns.ros.busToMsg.std_msgs.Header(slBusIn.Header,rosmsgOut.Header(1));
    rosmsgOut.NewVelocity = double(slBusIn.NewVelocity);
end
