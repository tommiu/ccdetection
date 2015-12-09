// checks whether a given node represents an assignment
Object.metaClass.isConcatAssignment = { it -> (
    it.getProperty("type") == TYPE_ASSIGN ||
    it.getProperty("type") == TYPE_ASSIGN_REF ||
    it.getProperty("type") == TYPE_ASSIGN_OP 
    ) && 
    it.hasFlag("ASSIGN_CONCAT")
}

