package dev.nihongolab.architecture;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import org.junit.jupiter.api.Test;

class ArchitectureRulesSelfTest {

    static final JavaClasses FIXTURES =
            new ClassFileImporter().importPackages("archfixture");

    @Test
    void domainRuleCatchesSpringDependency() {
        assertThatThrownBy(() -> ArchitectureRules.DOMAIN_IS_PURE.check(FIXTURES))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("SpringInDomain");
    }

    @Test
    void applicationRuleCatchesAdapterDependency() {
        assertThatThrownBy(() -> ArchitectureRules.APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER.check(FIXTURES))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("AdapterInApplication");
    }

    @Test
    void entityRuleCatchesEntityOutsidePersistenceAdapter() {
        assertThatThrownBy(() -> ArchitectureRules.ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER.check(FIXTURES))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("MisplacedEntity");
    }

    @Test
    void controllerRuleCatchesControllerOutsideWebAdapter() {
        assertThatThrownBy(() -> ArchitectureRules.CONTROLLERS_ONLY_IN_WEB_ADAPTER.check(FIXTURES))
                .isInstanceOf(AssertionError.class)
                .hasMessageContaining("MisplacedController");
    }
}
