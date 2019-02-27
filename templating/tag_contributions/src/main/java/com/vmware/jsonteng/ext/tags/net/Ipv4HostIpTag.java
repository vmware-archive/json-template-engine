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

public class Ipv4HostIpTag extends TagBase {
    public static final String name = "ipv4-host-ip";

    private final ElementResolver elementResolver;

    public Ipv4HostIpTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount < 2) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" needs at least 2 parameters. Parameters given %s", name, tagTokens));
        }
        String resolvedNetwork = (String) this.elementResolver.resolve(
                tagTokens.get(0), bindingDataList);
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
                tagTokens.get(1), bindingDataList).toString());
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
