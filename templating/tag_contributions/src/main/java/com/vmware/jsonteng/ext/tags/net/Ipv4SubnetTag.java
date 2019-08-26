package com.vmware.jsonteng.ext.tags.net;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;
import com.vmware.jsonteng.tags.TagBase;

public class Ipv4SubnetTag extends TagBase {
    public static final String name = "ipv4-subnet";

    private final ElementResolver elementResolver;

    public Ipv4SubnetTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount != 3) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 3 parameters. Parameters given %s", name, tagTokens));
        }
        String network = (String) this.elementResolver.resolve(tagTokens.get(0), bindingDataList);
        int subnetCount = Integer.parseInt(this.elementResolver.resolve(
                tagTokens.get(1), bindingDataList).toString());
        int subnetIndex = Integer.parseInt(this.elementResolver.resolve(
                tagTokens.get(2), bindingDataList).toString());
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
