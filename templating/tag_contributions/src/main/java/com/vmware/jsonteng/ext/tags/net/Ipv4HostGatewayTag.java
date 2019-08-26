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

public class Ipv4HostGatewayTag extends TagBase {
    public static final String name = "ipv4-host-gateway";

    private final ElementResolver elementResolver;

    public Ipv4HostGatewayTag(TagResolver TagResolver) {
        super(TagResolver);
        elementResolver = TagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount != 1) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 1 parameter. Parameters given %s", name, tagTokens));
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
        int gatewayInt = network + 1;
        fourBytes.rewind();
        fourBytes.putInt(gatewayInt);
        Inet4Address gateway;
        try {
            gateway = (Inet4Address) InetAddress.getByAddress(fourBytes.array());
        } catch (UnknownHostException e) {
            throw new TemplateEngineException("Unabled to get ip address " + fourBytes, e);
        }
        return gateway.getHostAddress();
    }
}
