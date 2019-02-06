package com.vmware.jsonteng.ext.rules.net;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;
import com.vmware.jsonteng.rules.RuleBase;

public class Ipv4HostIpRule extends RuleBase {
    public static final String name = "ipv4-host-ip";

    private final ElementResolver elementResolver;

    public Ipv4HostIpRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount < 2) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" needs at least 2 parameters. Parameters given %s", name, ruleTokens));
        }
        String resolvedNetwork = (String) this.elementResolver.resolve(
                ruleTokens.get(0), bindingDataList);
        String[] parts = resolvedNetwork.split("/");
        Inet4Address networkAddress;
        try {
            networkAddress = (Inet4Address) InetAddress.getByName(parts[0]);
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unable to get the network address " + parts[0], e);
        }
        ByteBuffer fourBytes = ByteBuffer.wrap(new byte[4]);
        fourBytes.put(networkAddress.getAddress());
        fourBytes.rewind();
        int network = fourBytes.getInt();
        int index = Integer.parseInt(this.elementResolver.resolve(
                ruleTokens.get(1), bindingDataList).toString());
        int prefix = Integer.parseInt(parts[1]);
        if (index == 0 || index >= (1 << (32 - prefix))) {
            throw new TemplateEngineException(index + " is out of ip range 2^" + prefix);
        }
        int ipAddressInt = network + index;
        fourBytes.rewind();
        fourBytes.putInt(ipAddressInt);
        Inet4Address ipAddress;
        try {
            ipAddress = (Inet4Address) InetAddress.getByAddress(fourBytes.array());
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unabled to get ip address " + fourBytes, e);
        }
        return ipAddress.getHostAddress();
    }
}
