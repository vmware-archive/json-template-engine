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

public class Ipv4HostNetmaskRule extends RuleBase {
    public static final String name = "ipv4-host-netmask";

    private final ElementResolver elementResolver;

    public Ipv4HostNetmaskRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount < 1) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" needs at least 1 parameters. Parameters given %s", name, ruleTokens));
        }
        String resolvedNetwork = (String) this.elementResolver.resolve(
                ruleTokens.get(0), bindingDataList);
        String[] parts = resolvedNetwork.split("/");
        int prefix = Integer.parseInt(parts[1]);
        ByteBuffer fourBytes = ByteBuffer.wrap(new byte[4]);
        int netmaskInt = 0xFFFFFFFF << (32 - prefix);
        fourBytes.putInt(netmaskInt);
        Inet4Address netmask;
        try {
            netmask = (Inet4Address) InetAddress.getByAddress(fourBytes.array());
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unable to get netmask " + fourBytes);
        }
        return netmask.getHostAddress();
    }
}
