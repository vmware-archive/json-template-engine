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

public class Ipv4SubnetRule extends RuleBase {
    public static final String name = "ipv4-subnet";

    private final ElementResolver elementResolver;

    public Ipv4SubnetRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount < 3) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" needs at least 3 parameters. Parameters given %s", name, ruleTokens));
        }
        String network = (String) this.elementResolver.resolve(ruleTokens.get(0), bindingDataList);
        int subnetCount = Integer.parseInt(this.elementResolver.resolve(
                ruleTokens.get(1), bindingDataList).toString());
        int subnetIndex = Integer.parseInt(this.elementResolver.resolve(
                ruleTokens.get(2), bindingDataList).toString());
        int base2Exp = 0;
        int count = subnetCount - 1;
        while ((count & 0x1) != 0) {
            count = count >>> 1;
            base2Exp += 1;
        }
        if (count != 0) {
            throw new TemplateEngineException(
                    String.format("Subnet count must be multiple of 2s. %d is given", subnetCount));
        }
        if (base2Exp == 0) {
            return network;
        }
        String[] parts = network.split("/");
        Inet4Address networkAddress;
        try {
            networkAddress = (Inet4Address) InetAddress.getByName(parts[0]);
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unable to parse ip address " + parts[0], e);
        }
        int networkPrefix = Integer.parseInt(parts[1]);
        int subnetPrefix = networkPrefix + base2Exp;
        ByteBuffer fourBytes = ByteBuffer.wrap(new byte[4]);
        fourBytes.put(networkAddress.getAddress());
        fourBytes.rewind();
        int networkBytes = fourBytes.getInt();
        int subnetBytes = networkBytes + (subnetIndex << (32 - subnetPrefix));
        fourBytes.rewind();
        fourBytes.putInt(subnetBytes);
        Inet4Address subnetAddress;
        try {
            subnetAddress = (Inet4Address) InetAddress.getByAddress(fourBytes.array());
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unable to partition subnet " + fourBytes.toString(), e);
        }
        return subnetAddress.getHostAddress() + '/' + Integer.toString(subnetPrefix);
    }
}
