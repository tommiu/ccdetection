// checks whether a given node represents an assignment
Object.metaClass.isConcatAssignment = { it -> (
    it.type == TYPE_ASSIGN ||
    it.type == TYPE_ASSIGN_REF ||
    it.type == TYPE_ASSIGN_OP 
    ) && 
    it.hasFlag("ASSIGN_CONCAT")
}

