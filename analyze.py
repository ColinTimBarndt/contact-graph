import networkx as nx

from data import PlatformContact, Contact, PlatformCommunity


class GraphBuilder:
    contacts: set[Contact]
    communities: set[PlatformCommunity]
    contact_by_name: dict[str, Contact]
    contact_by_phone: dict[str, Contact]

    def __init__(self):
        self.contacts = set()
        self.communities = set()
        self.contact_by_name = {}
        self.contact_by_phone = {}

    def find_related(self, contact: PlatformContact) -> set[Contact]:
        rel = set()
        dup_names = set()
        for name in contact.names:
            if name in self.contact_by_name:
                found = self.contact_by_name[name]
                if contact.platform in found.platforms:
                    del self.contact_by_name[name]
                    dup_names.add(name)
                else:
                    rel.add(found)
        for phone in contact.phones:
            if phone in self.contact_by_phone:
                found = self.contact_by_phone[phone]
                rel.add(found)
        no_dup_names = contact.names - dup_names
        for r in rel:
            r.names |= no_dup_names
        return rel

    def add(self, contacts: list[PlatformContact]):
        for pc in contacts:
            self.communities |= pc.communities
            related = self.find_related(pc)
            for rel in related:
                rel.platforms[pc.platform] = pc
                rel.communities |= pc.communities
                rel.personal |= pc.personal
            if len(related) == 0:
                contact = Contact()
                contact.platforms[pc.platform] = pc
                contact.names |= pc.names
                contact.communities |= pc.communities
                contact.personal = pc.personal
                self.contacts.add(contact)

                for name in pc.names:
                    self.contact_by_name[name] = contact
                for phone in pc.phones:
                    self.contact_by_phone[phone] = contact
        return self

    def build(self, *, usernames=True, personal_only=False) -> nx.Graph:
        graph = nx.Graph()
        graph.add_node("ME", type='me', name='me')

        for comm in self.communities:
            if personal_only and not comm.personal:
                continue
            graph.add_node(comm, name=comm.name)
            if comm.personal:
                graph.add_edge("ME", comm)

        for contact in self.contacts:
            if personal_only and not contact.personal:
                continue
            if len(contact.communities) < 2:
                continue
            if usernames:
                graph.add_node(contact, name=max(contact.names, key=len, default='UNKNOWN')[0:20])
            else:
                graph.add_node(contact, name='')
            if contact.personal:
                graph.add_edge("ME", contact, personal=True)
            for comm in contact.communities:
                graph.add_edge(contact, comm)

        return graph
