package dev.nihongolab.architecture;

import dev.nihongolab.NihongolabApplication;
import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;
import org.springframework.modulith.docs.Documenter;

class ModularityTest {

    static final ApplicationModules MODULES =
            ApplicationModules.of(NihongolabApplication.class);

    @Test
    void verifiesModularStructure() {
        MODULES.verify();
    }

    @Test
    void writesDocumentation() {
        new Documenter(MODULES).writeDocumentation();
    }
}
