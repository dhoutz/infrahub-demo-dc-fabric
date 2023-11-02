import logging
import uuid
from collections import defaultdict
from ipaddress import IPv4Network
from typing import Dict, List
from pprint import pprint 

from infrahub_client import UUIDT, InfrahubClient, InfrahubNode, NodeStore

# flake8: noqa
# pylint: skip-file

DEVICE_ROLES = ["spine", "leaf", "client"]
INTF_ROLES = ["backbone", "transit", "peering", "peer", "loopback", "management", "spare"]
VLAN_ROLES = ["server"]

SITE_NAMES = ["atl"]

PLATFORMS = (
    ("Cisco IOS", "ios", "ios", "cisco_ios", "ios"),
    ("Cisco NXOS SSH", "nxos_ssh", "nxos_ssh", "cisco_nxos", "nxos"),
    ("Juniper JunOS", "junos", "junos", "juniper_junos", "junos"),
    ("Arista EOS", "eos", "eos", "arista_eos", "eos"),
    ("Linux", "linux", "linux", "linux", "linux"),
)

DEVICES = (
    ("spine", "active", "7280R3", "profile1", "spine", ["red", "green"], "Arista EOS", 2),
    ("leaf", "active", "7280R3", "profile1", "leaf", ["red", "green"], "Arista EOS", 4),
    ("client", "active", "linux", "profile1", "client", ["red", "green"], "Linux", 2),
)


NETWORKS_POOL_INTERNAL = IPv4Network("10.0.0.0/8").subnets(new_prefix=16)
LOOPBACK_POOL = next(NETWORKS_POOL_INTERNAL).hosts()
P2P_NETWORK_POOL = next(NETWORKS_POOL_INTERNAL).subnets(new_prefix=31)
NETWORKS_POOL_EXTERNAL = IPv4Network("203.0.113.0/24").subnets(new_prefix=29)

MANAGEMENT_IPS = IPv4Network("172.20.20.16/28").hosts()


# P2P_NETWORKS_POOL = {
#     ("atl1", "edge1", "ord1", "edge1"): next(P2P_NETWORK_POOL).hosts(),
#     ("atl1", "edge1", "jfk1", "edge1"): next(P2P_NETWORK_POOL).hosts(),
#     ("jfk1", "edge1", "ord1", "edge1"): next(P2P_NETWORK_POOL).hosts(),
#     ("atl1", "edge2", "ord1", "edge2"): next(P2P_NETWORK_POOL).hosts(),
#     ("atl1", "edge2", "jfk1", "edge2"): next(P2P_NETWORK_POOL).hosts(),
#     ("jfk1", "edge2", "ord1", "edge2"): next(P2P_NETWORK_POOL).hosts(),
# }

BACKBONE_CIRCUIT_IDS = [
    "DUFF-1543451",
    "DUFF-6535773",
    "DUFF-5826854",
    "DUFF-8263953",
    "DUFF-7324064",
    "DUFF-4867430",
    "DUFF-4654456",
]

INTERFACE_MGMT_NAME = {"7280R3": "Management0", "ASR1002-HX": "Management0", "linux": "Eth0"}

INTERFACE_L3_NAMES = {
    "7280R3": [
        "Ethernet1",
        "Ethernet2",
        "Ethernet3",
        "Ethernet4",
        "Ethernet5",
        "Ethernet6",
        "Ethernet7",
        "Ethernet8",
        "Ethernet9",
        "Ethernet10",
    ],
    "ASR1002-HX": [
        "Ethernet1",
        "Ethernet2",
        "Ethernet3",
        "Ethernet4",
        "Ethernet5",
        "Ethernet6",
        "Ethernet7",
        "Ethernet8",
        "Ethernet9",
        "Ethernet10",
    ]
}
INTERFACE_L2_NAMES = {
    "7280R3": ["Ethernet11", "Ethernet12"],
    "ASR1002-HX": ["Ethernet11", "Ethernet12"],
    "linux": ["Eth1", "Eth2"],
}

INTERFACE_ROLES_MAPPING = {
    "spine": [
        "transit",
        "transit",
        "backbone",
        "backbone",
        "backbone",
        "backbone",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
    ],
    "leaf": [
        "peer",
        "peer",
        "backbone",
        "backbone",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
        "spare",
    ]
}

STATUSES = ["active", "provisionning", "maintenance", "drained"]

TAGS = ["blue", "green", "red"]

ORGANIZATIONS = (
    ["Telia", 1299],
    ["Colt", 8220],
    ["Verizon", 701],
    ["GTT", 3257],
    ["Hurricane Electric", 6939],
    ["Lumen", 3356],
    ["Zayo", 6461],
    ["Duff", 64496],
    ["Equinix", 24115],
)

INTERFACE_OBJS: Dict[str, List[InfrahubNode]] = defaultdict(list)

ACCOUNTS = (
    ("pop-builder", "Script", "Password123", "read-write"),
    ("CRM Synchronization", "Script", "Password123", "read-write"),
    ("Jack Bauer", "User", "Password123", "read-only"),
    ("Chloe O'Brian", "User", "Password123", "read-write"),
    ("David Palmer", "User", "Password123", "read-write"),
    ("Operation Team", "User", "Password123", "read-only"),
    ("Engineering Team", "User", "Password123", "read-write"),
    ("Architecture Team", "User", "Password123", "read-only"),
)


GROUPS = (
    ("edge_router", "Edge Router"),
    ("cisco_devices", "Cisco Devices"),
    ("arista_devices", "Arista Devices"),
    ("transit_interfaces", "Transit Interface"),
)

BGP_PEER_GROUPS = (
    ("POP_INTERNAL", "IMPORT_INTRA_POP", "EXPORT_INTRA_POP", "Duff", "Duff"),
    ("POP_GLOBAL", "IMPORT_POP_GLOBAL", "EXPORT_POP_GLOBLA", "Duff", None),
    ("TRANSIT_DEFAULT", "IMPORT_TRANSIT", "EXPORT_PUBLIC_PREFIX", "Duff", None),
    ("TRANSIT_TELIA", "IMPORT_TRANSIT", "EXPORT_PUBLIC_PREFIX", "Duff", "Telia"),
    ("IX_DEFAULT", "IMPORT_IX", "EXPORT_PUBLIC_PREFIX", "Duff", None),
)

VLANS = (
    ("200", "server"),
    ("400", "management"),
)

store = NodeStore()


async def group_add_member(client: InfrahubClient, group: InfrahubNode, members: List[InfrahubNode], branch: str):
    members_str = ["{ id: " + f'"{member.id}"' + " }" for member in members]
    query = """
    mutation {
        RelationshipAdd(
            data: {
                id: "%s",
                name: "members",
                nodes: [ %s ]
            }
        ) {
            ok
        }
    }
    """ % (
        group.id,
        ", ".join(members_str),
    )

    await client.execute_graphql(query=query, branch_name=branch)


async def generate_site(client: InfrahubClient, log: logging.Logger, branch: str, site_name: str):
    group_eng = store.get("Engineering Team")
    group_ops = store.get("Operation Team")
    account_pop = store.get("pop-builder")
    account_crm = store.get("CRM Synchronization")
    active_status = store.get(kind="BuiltinStatus", key="active")
    internal_as = store.get(kind="InfraAutonomousSystem", key="Duff")

    group_edge_router = store.get(kind="CoreStandardGroup", key="edge_router")
    group_cisco_devices = store.get(kind="CoreStandardGroup", key="cisco_devices")
    group_arista_devices = store.get(kind="CoreStandardGroup", key="arista_devices")
    group_transit_interfaces = store.get(kind="CoreStandardGroup", key="transit_interfaces")

    # --------------------------------------------------
    # Create the Site
    # --------------------------------------------------
    site = await client.create(
        branch=branch,
        kind="BuiltinLocation",
        name={"value": site_name, "is_protected": True, "source": account_crm.id},
        type={"value": "SITE", "is_protected": True, "source": account_crm.id},
    )
    await site.save()
    log.info(f"Created Site: {site_name}")

    peer_networks = {
        0: next(P2P_NETWORK_POOL).hosts(),
        1: next(P2P_NETWORK_POOL).hosts(),
        2: next(P2P_NETWORK_POOL).hosts(),
        3: next(P2P_NETWORK_POOL).hosts(),

    }

    # --------------------------------------------------
    # Create the site specific VLAN
    # --------------------------------------------------
    for vlan in VLANS:
        status_id = active_status.id
        role_id = store.get(kind="BuiltinRole", key=vlan[1]).id
        vlan_name = f"{site_name}_{vlan[1]}"
        obj = await client.create(
            branch=branch,
            kind="InfraVLAN",
            name={"value": f"{site_name}_{vlan[1]}", "is_protected": True, "source": account_pop.id},
            vlan_id={"value": int(vlan[0]), "is_protected": True, "owner": group_eng.id, "source": account_pop.id},
            status={"id": status_id, "owner": group_ops.id},
            role={"id": role_id, "source": account_pop.id, "is_protected": True, "owner": group_eng.id},
        )
        await obj.save()

        store.set(key=vlan_name, node=obj)

    for idx, device in enumerate(DEVICES):

        for id in range(1, device[7]+1):
            device_name = f"{site_name}-{device[0]}{id}"
            status_id = store.get(kind="BuiltinStatus", key=device[1]).id
            role_id = store.get(kind="BuiltinRole", key=device[4]).id
            device_type = device[2]
            platform_id = store.get(kind="InfraPlatform", key=device[6]).id

            obj = await client.create(
                branch=branch,
                kind="InfraDevice",
                site={"id": site.id, "source": account_pop.id, "is_protected": True},
                name={"value": device_name, "source": account_pop.id, "is_protected": True},
                status={"id": status_id, "owner": group_ops.id},
                type={"value": device[2], "source": account_pop.id},
                role={"id": role_id, "source": account_pop.id, "is_protected": True, "owner": group_eng.id},
                asn={"id": internal_as.id, "source": account_pop.id, "is_protected": True, "owner": group_eng.id},
                tags=[store.get(kind="BuiltinTag", key=tag_name).id for tag_name in device[5]],
                platform={"id": platform_id, "source": account_pop.id, "is_protected": True},
            )
            await obj.save()

            store.set(key=device_name, node=obj)
            log.info(f"- Created Device: {device_name}")

            # Add device to groups
            await group_add_member(client=client, group=group_edge_router, members=[obj], branch=branch)

            if "Arista" in device[6]:
                await group_add_member(client=client, group=group_arista_devices, members=[obj], branch=branch)
            elif "Cisco" in device[6]:
                await group_add_member(client=client, group=group_cisco_devices, members=[obj], branch=branch)

            # Loopback Interface
            intf = await client.create(
                branch=branch,
                kind="InfraInterfaceL3",
                device={"id": obj.id, "is_protected": True},
                name={"value": "Loopback0", "source": account_pop.id, "is_protected": True},
                enabled=True,
                status={"id": active_status.id, "owner": group_ops.id},
                role={
                    "id": store.get(kind="BuiltinRole", key="loopback").id,
                    "source": account_pop.id,
                    "is_protected": True,
                },
                speed=1000,
            )
            await intf.save()

            log.info(f"- Created loopback iface for: {device_name}")

            ip = await client.create(
                branch=branch,
                kind="InfraIPAddress",
                interface={"id": intf.id, "source": account_pop.id},
                address={"value": f"{str(next(LOOPBACK_POOL))}/32", "source": account_pop.id},
            )
            await ip.save()

            store.set(key=f"{device_name}-loopback", node=ip)

            log.info(f"- Created IP for loopback iface on: {device_name}")

            # Management Interface
            intf = await client.create(
                branch=branch,
                kind="InfraInterfaceL3",
                device={"id": obj.id, "is_protected": True},
                name={"value": INTERFACE_MGMT_NAME[device_type], "source": account_pop.id},
                enabled={"value": True, "owner": group_eng.id},
                status={"id": active_status.id, "owner": group_eng.id},
                role={
                    "id": store.get(kind="BuiltinRole", key="management").id,
                    "source": account_pop.id,
                    "is_protected": True,
                },
                speed=1000,
            )
            await intf.save()

            log.info(f"- Created mgmt iface for: {device_name}")

            ip = await client.create(
                branch=branch, kind="InfraIPAddress", interface=intf.id, address=f"{str(next(MANAGEMENT_IPS))}/24"
            )
            await ip.save()

            # set the IP address of the device to the management interface IP address
            obj.primary_address = ip
            await obj.save()

            log.info(f"- Created IP for mgmt iface on: {device_name}")

            # L3 Interfaces
            if device[4] in ["spine", "leaf"]:

                for intf_idx, intf_name in enumerate(INTERFACE_L3_NAMES[device_type]):
                    intf_role = INTERFACE_ROLES_MAPPING[device[4]][intf_idx]
                    intf_role_id = store.get(kind="BuiltinRole", key=intf_role).id

                    intf = await client.create(
                        branch=branch,
                        kind="InfraInterfaceL3",
                        device={"id": obj.id, "is_protected": True},
                        name=intf_name,
                        speed=10000,
                        enabled=True,
                        status={"id": active_status.id, "owner": group_ops.id},
                        role={"id": intf_role_id, "source": account_pop.id},
                    )
                    await intf.save()

                    store.set(key=f"{device_name}-l3-{intf_idx}", node=intf)
                    INTERFACE_OBJS[device_name].append(intf)

                    # address = None
                    # if intf_role == "peer":
                    #     address = f"{str(next(peer_networks[intf_idx]))}/31"

                    # if intf_role == "backbone":
                    #     site_idx = intf_idx - 2
                    #     other_site_name = other_sites[site_idx]
                    #     sites = sorted([site_name, other_site_name])
                    #     link_id = (sites[0], device[0], sites[1], device[0])
                    #     address = f"{str(next(P2P_NETWORKS_POOL[link_id]))}/31"

                    if intf_role in ["transit", "peering"]:
                        subnet = next(NETWORKS_POOL_EXTERNAL).hosts()
                        address = f"{str(next(subnet))}/29"
                        peer_address = f"{str(next(subnet))}/29"

                    if not address:
                        continue

                    if address:
                        ip = await client.create(
                            branch=branch,
                            kind="InfraIPAddress",
                            interface={"id": intf.id, "source": account_pop.id},
                            address={"value": address, "source": account_pop.id},
                        )
                        await ip.save()

                    log.info(f"- Created iface: {device_name}-l3-{intf_idx} on: {device_name}")

                    # Create Circuit and BGP session for transit and peering
                    if intf_role in ["transit", "peering"]:
                        circuit_id_unique = str(uuid.UUID(int=abs(hash(f"{device_name}-{intf_role}-{address}"))))[24:]
                        circuit_id = f"DUFF-{circuit_id_unique}"
                        transit_providers = ["Telia", "Colt"]

                        if intf_role == "transit":
                            provider_name = transit_providers[intf_idx % 2]
                        elif intf_role == "peering":
                            provider_name = "Equinix"

                        provider = store.get(kind="CoreOrganization", key=provider_name)

                        circuit = await client.create(
                            branch=branch,
                            kind="InfraCircuit",
                            circuit_id=circuit_id,
                            vendor_id=f"{provider_name.upper()}-{UUIDT().short()}",
                            provider=provider.id,
                            status={"id": active_status.id, "owner": group_ops.id},
                            role={
                                "id": store.get(kind="BuiltinRole", key=intf_role).id,
                                "source": account_pop.id,
                                "owner": group_eng.id,
                            },
                        )
                        await circuit.save()

                        endpoint1 = await client.create(
                            branch=branch,
                            kind="InfraCircuitEndpoint",
                            site=site,
                            circuit=circuit.id,
                            connected_interface=intf.id,
                        )
                        await endpoint1.save()

                        intf.description.value = f"Connected to {provider_name} via {circuit_id}"

                        if intf_role == "transit":
                            peer_group_name = "TRANSIT_TELIA" if "telia" in provider.name.value.lower() else "TRANSIT_DEFAULT"

                            peer_ip = await client.create(
                                branch=branch,
                                kind="InfraIPAddress",
                                address=peer_address,
                            )
                            await peer_ip.save()

                            peer_as = store.get(kind="InfraAutonomousSystem", key=provider_name)
                            bgp_session = await client.create(
                                branch=branch,
                                kind="InfraBGPSession",
                                type="EXTERNAL",
                                local_as=internal_as.id,
                                local_ip=ip.id,
                                remote_as=peer_as.id,
                                remote_ip=peer_ip.id,
                                peer_group=store.get(key=peer_group_name).id,
                                device=store.get(key=device_name).id,
                                status=active_status.id,
                                role=store.get(kind="BuiltinRole", key=intf_role).id,
                            )
                            await bgp_session.save()

                            log.info(
                                f" Created BGP Session '{device_name}' >> '{provider_name}': '{peer_group_name}' '{ip.address.value}' >> '{peer_ip.address.value}'"
                            )

            # L2 Interfaces
            for intf_idx, intf_name in enumerate(INTERFACE_L2_NAMES[device_type]):
                intf_role_id = store.get(kind="BuiltinRole", key="server").id

                intf = await client.create(
                    branch=branch,
                    kind="InfraInterfaceL2",
                    device={"id": obj.id, "is_protected": True},
                    name=intf_name,
                    speed=10000,
                    enabled=True,
                    status={"id": active_status.id, "owner": group_ops.id},
                    role={"id": intf_role_id, "source": account_pop.id},
                    l2_mode="Access",
                    untagged_vlan={"id": store.get(kind="InfraVLAN", key=f"{site_name}_server").id},
                )
                await intf.save()

    # --------------------------------------------------
    # Connect each leave to each spine
    # --------------------------------------------------

    for spine_id in range(1,3):
        for leaf_id in range(1, 5):
            intf_spine = store.get(kind="InfraInterfaceL3", key=f"{site_name}-spine{spine_id}-l3-{leaf_id+1}")
            intf_leaf = store.get(kind="InfraInterfaceL3", key=f"{site_name}-leaf{leaf_id}-l3-{spine_id+1}")

            intf_leaf.description.value = f"Connected to {site_name}-spine{spine_id} {intf_spine.name.value}"
            await intf_leaf.save()
            intf_spine.description.value = f"Connected to {site_name}-leaf{leaf_id} {intf_leaf.name.value}"
            await intf_spine.save()
            log.info(f"Connected  '{site_name}-leaf{leaf_id}::{intf_leaf.name.value}' <> '{site_name}-spine{spine_id}::{intf_spine.name.value}'")


    # --------------------------------------------------
    # Create iBGP Sessions within the Site
    # --------------------------------------------------

    for spine_id in range(1,3):
        for leaf_id in range(1, 5):
            device1 = f"{site_name}-spine{spine_id}"
            device2 = f"{site_name}-leaf{leaf_id}"

            peer_group_name = "POP_INTERNAL"

            loopback1 = store.get(key=f"{device1}-loopback")
            loopback2 = store.get(key=f"{device2}-loopback")

            obj = await client.create(
                branch=branch,
                kind="InfraBGPSession",
                type="INTERNAL",
                local_as=internal_as.id,
                local_ip=loopback1.id,
                remote_as=internal_as.id,
                remote_ip=loopback2.id,
                peer_group=store.get(key=peer_group_name).id,
                device=store.get(kind="InfraDevice", key=device1).id,
                status=active_status.id,
                role=store.get(kind="BuiltinRole", key="backbone").id,
            )
            await obj.save()

            log.info(
                f" Created BGP Session '{device1}' >> '{device2}': '{peer_group_name}' '{loopback1.address.value}' >> '{loopback2.address.value}'"
            )

    return site_name


async def branch_scenario_add_transit(client: InfrahubClient, log: logging.Logger, site_name: str):
    """
    Create a new branch and Add a new transit link with GTT on the leaf1 device of the given site.
    """
    device_name = f"{site_name}-leaf1"

    new_branch_name = f"{site_name}-add-transit"
    new_branch = await client.branch.create(
        branch_name=new_branch_name, data_only=True, description=f"Add a new Transit link in {site_name}"
    )
    log.info(f"Created branch: {new_branch_name!r}")

    # Querying the object for now, need to pull from the store instead
    site = await client.get(branch=new_branch_name, kind="BuiltinLocation", name__value=site_name)

    device = await client.get(branch=new_branch_name, kind="InfraDevice", name__value=device_name)
    active_status = await client.get(branch=new_branch_name, kind="BuiltinStatus", name__value="active")
    role_transit = await client.get(branch=new_branch_name, kind="BuiltinRole", name__value="transit")
    role_spare = await client.get(branch=new_branch_name, kind="BuiltinRole", name__value="spare")
    gtt_organization = await client.get(branch=new_branch_name, kind="CoreOrganization", name__value="GTT")

    store.set(key="active", node=active_status)
    store.set(key="transit", node=role_transit)
    store.set(key="GTT", node=gtt_organization)

    intfs = await client.filters(
        branch=new_branch_name, kind="InfraInterfaceL3", device__ids=[device.id], role__ids=[role_spare.id]
    )
    intf = intfs[0]
    log.info(f" Adding new Transit on '{device_name}::{intf.name.value}'")

    # Allocate a new subnet and calculate new IP Addresses
    subnet = next(NETWORKS_POOL_EXTERNAL).hosts()
    address = f"{str(next(subnet))}/29"
    peer_address = f"{str(next(subnet))}/29"

    peer_ip = await client.create(
        branch=new_branch_name,
        kind="InfraIPAddress",
        address=peer_address,
    )
    await peer_ip.save()

    ip = await client.create(
        branch=new_branch_name,
        kind="InfraIPAddress",
        interface={"id": intf.id},
        address={"value": address},
    )
    await ip.save()

    provider = store.get(kind="CoreOrganization", key="GTT")
    circuit_id_unique = str(uuid.UUID(int=abs(hash(f"{device_name}-transit-{address}"))))[24:]
    circuit_id = f"DUFF-{circuit_id_unique}"

    circuit = await client.create(
        branch=new_branch_name,
        kind="InfraCircuit",
        circuit_id=circuit_id,
        vendor_id=f"{provider.name.value.upper()}-{UUIDT().short()}",
        provider=provider.id,
        status={"id": active_status.id},  # "owner": group_ops.id},
        role={
            "id": store.get(kind="BuiltinRole", key="transit").id,
            # "source": account_pop.id,
            # "owner": group_eng.id,
        },
    )
    await circuit.save()

    endpoint1 = await client.create(
        branch=new_branch_name,
        kind="InfraCircuitEndpoint",
        site=site,
        circuit=circuit.id,
        connected_interface=intf.id,
    )
    await endpoint1.save()

    intf.description.value = f"Connected to {provider.name.value} via {circuit_id}"
    await intf.save()

    # Create BGP Session

    # Create Circuit
    # Create IP address
    # Change Role
    # Change description

    # peer_group_name = "TRANSIT_DEFAULT"

    #     peer_as = store.get(kind="InfraAutonomousSystem", key=provider_name)
    #     bgp_session = await client.create(
    #         branch=branch,
    #         kind="InfraBGPSession",
    #         type="EXTERNAL",
    #         local_as=internal_as.id,
    #         local_ip=ip.id,
    #         remote_as=peer_as.id,
    #         remote_ip=peer_ip.id,
    #         peer_group=store.get(key=peer_group_name).id,
    #         device=store.get(key=device_name).id,
    #         status=active_status.id,
    #         role=store.get(kind="BuiltinRole", key=intf_role).id,
    #     )
    #     await bgp_session.save()

    #     log.info(
    #         f" Created BGP Session '{device_name}' >> '{provider_name}': '{peer_group_name}' '{ip.address.value}' >> '{peer_ip.address.value}'"
    #     )


async def branch_scenario_replace_ip_addresses(client: InfrahubClient, log: logging.Logger, site_name: str):
    """
    Create a new Branch and Change the IP addresses between leaf1 and leaf2 on the selected site
    """
    device1_name = f"{site_name}-leaf1"
    device2_name = f"{site_name}-leaf2"

    new_branch_name = f"{site_name}-update-edge-ips"
    new_branch = await client.branch.create(
        branch_name=new_branch_name,
        data_only=True,
        description=f"Change the IP addresses between leaf1 and leaf2 in {site_name}",
    )
    log.info(f"Created branch: {new_branch_name!r}")

    new_peer_network = next(P2P_NETWORK_POOL).hosts()

    # site = await client.get(branch=new_branch_name, kind="BuiltinLocation", name__value=site_name)
    device1 = await client.get(branch=new_branch_name, kind="InfraDevice", name__value=device1_name)
    device2 = await client.get(branch=new_branch_name, kind="InfraDevice", name__value=device2_name)
    role_peer = await client.get(branch=new_branch_name, kind="BuiltinRole", name__value="peer")

    peer_intfs_dev1 = sorted(
        await client.filters(
            branch=new_branch_name, kind="InfraInterfaceL3", device__ids=[device1.id], role__ids=[role_peer.id]
        ),
        key=lambda x: x.name.value,
    )
    peer_intfs_dev2 = sorted(
        await client.filters(
            branch=new_branch_name, kind="InfraInterfaceL3", device__ids=[device2.id], role__ids=[role_peer.id]
        ),
        key=lambda x: x.name.value,
    )

    # Querying the object for now, need to pull from the store instead
    peer_ip = await client.create(
        branch=new_branch_name,
        kind="InfraIPAddress",
        interface={"id": peer_intfs_dev1[0].id},
        address=f"{str(next(new_peer_network))}/31",
    )
    await peer_ip.save()

    ip = await client.create(
        branch=new_branch_name,
        kind="InfraIPAddress",
        interface={"id": peer_intfs_dev2[0].id},  # , "source": account_pop.id},
        address={"value": f"{str(next(new_peer_network))}/31"},  # , "source": account_pop.id},
    )
    await ip.save()


async def branch_scenario_remove_colt(client: InfrahubClient, log: logging.Logger, site_name: str):
    """
    Create a new Branch and Delete both Transit Circuit with Colt
    """
    new_branch_name = f"{site_name}-delete-transit"
    new_branch = await client.branch.create(
        branch_name=new_branch_name, data_only=True, description=f"Delete transit circuit with colt in {site_name}"
    )
    log.info(f"Created branch: {new_branch_name!r}")

    spare = await client.get(branch=new_branch_name, kind="BuiltinRole", name__value="peer")

    # TODO need to update the role on the interface and need to delete the IP Address
    # for idx in range(1, 3):
    #     device_name = f"{site_name}-edge{idx}"
    #     device = await client.get(branch=new_branch_name, kind="InfraDevice", name__value=device_name)
    #     intf = await client.get(branch=new_branch_name, kind="InfraInterfaceL3", device__id=device.id, name__value="Ethernet5")

    # Delete circuits
    get_circuits_query = """
    query($site_name: String!) {
        InfraCircuitEndpoint(site__name__value: $site_name) {
            edges {
                node {
                    id
                    circuit {
                        node {
                            id
                            circuit_id {
                                value
                            }
                            provider {
                                node {
                                    name {
                                        value
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    circuits = await client.execute_graphql(
        branch_name=new_branch_name, query=get_circuits_query, variables={"site_name": site_name}
    )
    colt_circuits = [
        circuit
        for circuit in circuits["InfraCircuitEndpoint"]["edges"]
        if circuit["node"]["circuit"]["node"]["provider"]["node"]["name"]["value"] == "Colt"
    ]

    for item in colt_circuits:
        circuit_endpoint = await client.get(branch=new_branch_name, kind="InfraCircuitEndpoint", id=item["node"]["id"])
        await circuit_endpoint.delete()

        circuit = await client.get(
            branch=new_branch_name, kind="InfraCircuit", id=item["node"]["circuit"]["node"]["id"]
        )
        await circuit.delete()


async def branch_scenario_conflict_device(client: InfrahubClient, log: logging.Logger, site_name: str):
    """
    Create a new Branch and introduce some conflicts
    """
    device1_name = f"{site_name}-leaf1"
    f"{site_name}-leaf2"

    new_branch_name = f"{site_name}-maintenance-conflict"
    new_branch = await client.branch.create(
        branch_name=new_branch_name,
        data_only=True,
        description=f"Put {device1_name} in maintenance mode",
    )
    log.info(f"Created branch: {new_branch_name!r}")

    maintenance_status = store.get(key="maintenance")
    provisionning_status = store.get(key="provisionning")
    drained_status = store.get(key="drained")

    # Update Device 1 Status both in the Branch and in Main
    device1_branch = await client.get(branch=new_branch_name, kind="InfraDevice", name__value=device1_name)

    device1_branch.status = maintenance_status
    await device1_branch.save()

    intf1_branch = await client.get(
        branch=new_branch_name, kind="InfraInterfaceL3", device__ids=[device1_branch.id], name__value="Ethernet1"
    )
    intf1_branch.enabled.value = False
    intf1_branch.status = drained_status
    await intf1_branch.save()

    device1_main = await client.get(kind="InfraDevice", name__value=device1_name)

    device1_main.status = provisionning_status
    await device1_main.save()

    intf1_main = await client.get(kind="InfraInterfaceL3", device__ids=[device1_branch.id], name__value="Ethernet1")
    intf1_main.enabled.value = False
    await intf1_main.save()


async def branch_scenario_conflict_platform(client: InfrahubClient, log: logging.Logger):
    """
    Create a new Branch and introduce some conflicts on the platforms for node ADD and DELETE
    """
    new_branch_name = f"platform-conflict"
    new_branch = await client.branch.create(
        branch_name=new_branch_name,
        data_only=True,
        description=f"Add new platform",
    )
    log.info(f"Created branch: {new_branch_name!r}")

    # Create a new Platform object with the same name, both in the branch and in main
    platform1_branch = await client.create(
        branch=new_branch_name, kind="InfraPlatform", name="Cisco IOS XR", netmiko_device_type="cisco_xr"
    )
    await platform1_branch.save()
    platform1_main = await client.create(kind="InfraPlatform", name="Cisco IOS XR", netmiko_device_type="cisco_xr")
    await platform1_main.save()

    # Delete an existing Platform object on both in the Branch and in Main
    platform2_branch = await client.get(branch=new_branch_name, kind="InfraPlatform", name__value="Cisco NXOS SSH")
    await platform2_branch.delete()
    platform2_main = await client.get(kind="InfraPlatform", name__value="Cisco NXOS SSH")
    await platform2_main.delete()

    # Delete an existing Platform object in the branch and update it in main
    platform3_branch = await client.get(branch=new_branch_name, kind="InfraPlatform", name__value="Juniper JunOS")
    await platform3_branch.delete()
    platform3_main = await client.get(kind="InfraPlatform", name__value="Juniper JunOS")
    platform3_main.nornir_platform.value = "juniper_junos"
    await platform3_main.save()


# ---------------------------------------------------------------
# Use the `infrahubctl run` command line to execute this script
#
#   infrahubctl run models/infrastructure_edge.py
#
# ---------------------------------------------------------------
async def run(client: InfrahubClient, log: logging.Logger, branch: str):
    # ------------------------------------------
    # Create User Accounts, Groups & Organizations & Platforms
    # ------------------------------------------
    batch = await client.create_batch()

    for group in GROUPS:
        obj = await client.create(branch=branch, kind="CoreStandardGroup", data={"name": group[0], "label": group[1]})

        batch.add(task=obj.save, node=obj)
        store.set(key=group[0], node=obj)

    for account in ACCOUNTS:
        obj = await client.create(
            branch=branch,
            kind="CoreAccount",
            data={"name": account[0], "password": account[2], "type": account[1], "role": account[3]},
        )
        batch.add(task=obj.save, node=obj)
        store.set(key=account[0], node=obj)

    for org in ORGANIZATIONS:
        obj = await client.create(
            branch=branch, kind="CoreOrganization", data={"name": {"value": org[0], "is_protected": True}}
        )
        batch.add(task=obj.save, node=obj)
        store.set(key=org[0], node=obj)

    for platform in PLATFORMS:
        obj = await client.create(
            branch=branch,
            kind="InfraPlatform",
            data={
                "name": platform[0],
                "nornir_platform": platform[1],
                "napalm_driver": platform[2],
                "netmiko_device_type": platform[3],
                "ansible_network_os": platform[4],
            },
        )
        batch.add(task=obj.save, node=obj)
        store.set(key=platform[0], node=obj)

    # Create all Groups, Accounts and Organizations
    async for node, _ in batch.execute():
        log.info(f"{node._schema.kind} Created {node.name.value}")

    account_pop = store.get("pop-builder")
    account_cloe = store.get("Chloe O'Brian")

    # ------------------------------------------
    # Create Autonommous Systems
    # ------------------------------------------
    batch = await client.create_batch()
    for org in ORGANIZATIONS:
        obj = await client.create(
            branch=branch,
            kind="InfraAutonomousSystem",
            data={
                "name": {"value": f"AS{org[1]}", "source": account_pop.id, "owner": account_cloe.id},
                "asn": {"value": org[1], "source": account_pop.id, "owner": account_cloe.id},
                "organization": {"id": store.get(kind="CoreOrganization", key=org[0]).id, "source": account_pop.id},
            },
        )
        batch.add(task=obj.save, node=obj)
        store.set(key=org[0], node=obj)

    async for node, _ in batch.execute():
        log.info(f"{node._schema.kind} Created {node.name.value}")

    # ------------------------------------------
    # Create BGP Peer Groups
    # ------------------------------------------
    batch = await client.create_batch()
    for peer_group in BGP_PEER_GROUPS:
        remote_as_id = None
        remote_as = store.get(kind="InfraAutonomousSystem", key=peer_group[4], raise_when_missing=False)
        if remote_as:
            remote_as_id = remote_as.id

        obj = await client.create(
            branch=branch,
            kind="InfraBGPPeerGroup",
            name={"value": peer_group[0], "source": account_pop.id},
            import_policies={"value": peer_group[1], "source": account_pop.id},
            export_policies={"value": peer_group[2], "source": account_pop.id},
            local_as=store.get(kind="InfraAutonomousSystem", key=peer_group[3]).id,
            remote_as=remote_as_id,
        )
        batch.add(task=obj.save, node=obj)
        store.set(key=peer_group[0], node=obj)

    async for node, _ in batch.execute():
        log.info(f"Peer Group Created Created {node.name.value}")

    # ------------------------------------------
    # Create Status, Role & Tags
    # ------------------------------------------
    batch = await client.create_batch()

    log.info("Creating Roles, Status & Tag")
    for role in DEVICE_ROLES + INTF_ROLES + VLAN_ROLES:
        obj = await client.create(branch=branch, kind="BuiltinRole", name={"value": role, "source": account_pop.id})
        batch.add(task=obj.save, node=obj)
        store.set(key=role, node=obj)

    for status in STATUSES:
        obj = await client.create(branch=branch, kind="BuiltinStatus", name={"value": status, "source": account_pop.id})
        batch.add(task=obj.save, node=obj)
        store.set(key=status, node=obj)

    for tag in TAGS:
        obj = await client.create(branch=branch, kind="BuiltinTag", name={"value": tag, "source": account_pop.id})
        batch.add(task=obj.save, node=obj)
        store.set(key=tag, node=obj)

    async for node, _ in batch.execute():
        log.info(f"{node._schema.kind}  Created {node.name.value}")

    active_status = store.get(kind="BuiltinStatus", key="active")
    internal_as = store.get(kind="InfraAutonomousSystem", key="Duff")

    # ------------------------------------------
    # Create Sites
    # ------------------------------------------
    log.info("Creating Site & Device")

    batch = await client.create_batch()

    for site_name in SITE_NAMES:
        batch.add(task=generate_site, site_name=site_name, client=client, branch=branch, log=log)

    async for _, response in batch.execute():
        log.debug(f"Site {response} Creation Completed")

    # --------------------------------------------------
    # CREATE Full Mesh iBGP SESSION between all the Edge devices
    # --------------------------------------------------
    batch = await client.create_batch()
    for site1 in SITE_NAMES:
        for site2 in SITE_NAMES:
            if site1 == site2:
                continue

            for idx1 in range(1, 3):
                for idx2 in range(1, 3):
                    device1 = f"{site1}-leaf{idx1}"
                    device2 = f"{site2}-leaf{idx2}"

                    loopback1 = store.get(key=f"{device1}-loopback")
                    loopback2 = store.get(key=f"{device2}-loopback")

                    peer_group_name = "POP_GLOBAL"

                    obj = await client.create(
                        branch=branch,
                        kind="InfraBGPSession",
                        type="INTERNAL",
                        local_as=internal_as.id,
                        local_ip=loopback1.id,
                        remote_as=internal_as.id,
                        remote_ip=loopback2.id,
                        peer_group=store.get(key=peer_group_name).id,
                        device=store.get(kind="InfraDevice", key=device1).id,
                        status=active_status.id,
                        role=store.get(kind="BuiltinRole", key="backbone").id,
                    )
                    batch.add(task=obj.save, node=obj)
                    log.info(
                        f"Creating BGP Session '{device1}' >> '{device2}': '{peer_group_name}' '{loopback1.address.value}' >> '{loopback2.address.value}'"
                    )

    async for node, _ in batch.execute():
        log.debug(f"BGP Session Creation Completed")

    # --------------------------------------------------
    # CREATE BACKBONE LINKS & CIRCUITS
    # --------------------------------------------------
    # for idx, backbone_link in enumerate(P2P_NETWORKS_POOL.keys()):
    #     site1 = backbone_link[0]
    #     site2 = backbone_link[2]
    #     device = backbone_link[1]

    #     # Build a new list with the names of the other sites for later
    #     other_site_site1 = copy.copy(SITES)
    #     other_site_site1.remove(site1)
    #     other_site_site1 = sorted(other_site_site1)

    #     other_site_site2 = copy.copy(SITES)
    #     other_site_site2.remove(site2)
    #     other_site_site2 = sorted(other_site_site2)

    #     intf1 = INTERFACE_OBJS[f"{site1}-{device}"][other_site_site1.index(site2) + 2]
    #     intf2 = INTERFACE_OBJS[f"{site2}-{device}"][other_site_site2.index(site1) + 2]

    #     circuit_id = BACKBONE_CIRCUIT_IDS[idx]

    #     if idx <= 2:
    #         provider_name = "Lumen"
    #     else:
    #         provider_name = "Zayo"

    #     provider = store.get(kind="BuiltinOrganization", key=provider_name)
    #     obj = await client.create(
    #         branch=branch,
    #         kind="InfraCircuit",
    #         circuit_id=BACKBONE_CIRCUIT_IDS[idx],
    #         vendor_id=f"{provider_name.upper()}-{UUIDT().short()}",
    #         provider=provider,
    #         # type="DARK FIBER",
    #         status=active_status,
    #         role=store.get(kind="BuiltinRole", key="backbone"),
    #     )
    #     await obj.save()

    #     endpoint1 = await client.create(
    #         branch=branch, kind="InfraCircuitEndpoint", site=site1, circuit=obj, connected_endpoint=intf1
    #     )
    #     await endpoint1.save()
    #     endpoint2 = await client.create(
    #         branch=branch, kind="InfraCircuitEndpoint", site=site2, circuit=obj, connected_endpoint=intf2
    #     )
    #     await endpoint2.save()

    #     intf11 = await client.get(branch=branch, kind="InfraInterfaceL3", id=intf1.id)

    #     intf11.description.value = f"Connected to {site2}-{device} via {circuit_id}"
    #     await intf11.save()

    #     intf21 = await client.get(branch=branch, kind="InfraInterfaceL3", id=intf2.id)
    #     intf21.description.value = f"Connected to {site1}-{device} via {circuit_id}"
    #     await intf21.save()

    #     log.info(f"Connected  '{site1}-{device}::{intf1.name.value}' <> '{site2}-{device}::{intf2.name.value}'")

    # --------------------------------------------------
    # Create some changes in additional branches
    #  Scenario 1 - Add a Peering
    #  Scenario 2 - Change the IP Address between 2 edges
    #  Scenario 3 - Delete a Circuit + Peering
    #  Scenario 4 - Create some Relatioinship One and Attribute conflicts on a device
    #  Scenario 5 - Create some Node ADD and DELETE conflicts on some platform objects
    # --------------------------------------------------
    # if branch == "main":
    #     await branch_scenario_add_transit(
    #         site_name=SITE_NAMES[1],
    #         client=client,
    #         log=log,
    #     )
    #     await branch_scenario_replace_ip_addresses(site_name=SITE_NAMES[2], client=client, log=log)
    #     await branch_scenario_remove_colt(site_name=SITE_NAMES[0], client=client, log=log)
    #     await branch_scenario_conflict_device(site_name=SITE_NAMES[3], client=client, log=log)
    #     await branch_scenario_conflict_platform(client=client, log=log)