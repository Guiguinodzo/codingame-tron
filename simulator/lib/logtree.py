import re
import sys

TREE_BRANCH="\u251c" # ├
TREE_FINAL_BRANCH= "\u2514" # └
TREE_INTERMEDIATE_LINE="\u252c" # ┬
TREE_DASH="\u2500" # ─

TREE_INDENT_SIZE=2

ID_PATTERN = re.compile(r"#(\.[\w+-]+)*")

class LogTree:
    def __init__(self, id, log):
        self.id = id
        self.children = []
        self.logs = [log]

    def insert(self, id, log):
        if self.id == id:
            self.logs.append(log)
            return self

        if id in self.id:
            parent = LogTree(id, log)
            parent.children.append(self)
            return parent

        if not self.id in id:
            raise Exception(f"Wrong way: {id} is not a child of {self.id}")

        matching_child = None
        matching_child_index = None
        for (index, child) in enumerate(self.children):
            if child.id in id:
                matching_child = child
                matching_child_index = index
                break

        if matching_child is None:
            child = LogTree(id, log)
            self.children.append(child)
        else:
            returned_child = matching_child.insert(id, log)
            if returned_child != matching_child:
                self.children[matching_child_index] = returned_child

        return self

    def print(self, indent="", writer=print):
        last_id_fragment = self.id.split('.')[-1]
        writer(f"{indent}{last_id_fragment} : {self.logs[0]}")
        for idx, log in enumerate(self.logs[1:]):
            # last = idx == len(self.logs) - 2
            writer(f"{indent}{last_id_fragment} : {log}")

        for idx, child in enumerate(self.children):
            # last = idx == len(self.children) - 1
            child.print(indent + (" "*TREE_INDENT_SIZE), writer)



def parse_logs(logs: list[str]) -> LogTree:
    tree = None
    for log in [l[:-1] for l in logs]:
        id_match = ID_PATTERN.search(log)
        if id_match is None:
            print(f"Not a tree log: {log}")
            continue
        log_id = id_match.group(0)
        print(f"log_id: {log_id}")
        if tree is None:
            tree = LogTree(log_id, log)
        else:
            tree = tree.insert(log_id, log)
    return tree



def main():
    filename = sys.argv[1]

    with open(filename, 'r') as f:
        logs = f.readlines()
        log_tree = parse_logs(logs)
        if log_tree is not None:
            log_tree.print()
        else:
            print(f"No tree log found in {filename}")


if __name__ == '__main__':
    main()
