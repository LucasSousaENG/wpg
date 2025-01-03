function rosmsgOut = defuzzy_lcs(slBusIn, rosmsgOut)
%#codegen
%   Copyright 2021 The MathWorks, Inc.
    rosmsgOut.Header = bus_conv_fcns.ros.busToMsg.std_msgs.Header(slBusIn.Header,rosmsgOut.Header(1));
    rosmsgOut.NewP = double(slBusIn.NewP);
    rosmsgOut.NewI = double(slBusIn.NewI);
    rosmsgOut.NewD = double(slBusIn.NewD);
end
