import re
import sys

TREE_BRANCH = "\u251c"  # ├
TREE_FINAL_BRANCH = "\u2514"  # └
TREE_INTERMEDIATE_LINE = "\u252c"  # ┬
TREE_DASH = "\u2500"  # ─

TREE_INDENT_SIZE = 4

ID_PATTERN = re.compile(r"#\d*(\.[\w+-]+)*")


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

    def print_tree(self, indent="", writer=print):
        last_id_fragment = self.id.split('.')[-1]
        writer(f"{indent}{last_id_fragment} : {self.logs[0]}")
        for idx, log in enumerate(self.logs[1:]):
            # last = idx == len(self.logs) - 2
            writer(f"{indent}{last_id_fragment} : {log}")

        for idx, child in enumerate(self.children):
            # last = idx == len(self.children) - 1
            child.print(indent + (" " * TREE_INDENT_SIZE), writer)

    def find_and_print(self, log_id, log, indent="", writer=print):
        if log_id == self.id:
            last_id_fragment = self.id.split('.')[-1]
            writer(f"{indent}{last_id_fragment} : {log}")
        elif self.id in log_id:
            matching_child = None
            for (index, child) in enumerate(self.children):
                if child.id in log_id:
                    matching_child = child
                    break
            matching_child.find_and_print(log_id, log, indent + (" " * TREE_INDENT_SIZE), writer)
        else:
            writer(f"Not found {log_id} : got as far as {self.id}")


def parse_logs(logs: list[str]) -> LogTree:
    tree = LogTree("", "init")
    for log in [l[:-1] for l in logs]:
        log_id = parse_id(log)
        if log_id is None:
            # print(f"Not a tree log: {log}")
            continue
        # print(f"log_id: {log_id}")
        if tree is None:
            tree = LogTree(log_id, log)
        else:
            tree = tree.insert(log_id, log)
    return tree


def parse_id(log):
    id_match = ID_PATTERN.search(log)
    if id_match is not None:
        return id_match.group(0)
    else:
        return None


def main():
    filename = sys.argv[1]

    with open(filename, 'r') as f:
        logs = f.readlines()
        log_tree = parse_logs(logs)
        if log_tree is not None:
            for log in [l[:-1] for l in logs]:
                log_id = parse_id(log)
                if log_id is not None and log_id != "":
                    log_tree.find_and_print(log_id, log)
        else:
            print(f"No tree log found in {filename}")


if __name__ == '__main__':
    main()
