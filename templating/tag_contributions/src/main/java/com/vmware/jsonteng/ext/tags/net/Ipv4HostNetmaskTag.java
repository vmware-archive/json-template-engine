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

public class Ipv4HostNetmaskTag extends TagBase {
    public static final String name = "ipv4-host-netmask";

    private final ElementResolver elementResolver;

    public Ipv4HostNetmaskTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount < 1) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 1 parameter. Parameters given %s", name, tagTokens));
        }
        String resolvedNetwork = (String) this.elementResolver.resolve(
                tagTokens.get(0), bindingDataList);
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
