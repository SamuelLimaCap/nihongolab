package dev.nihongolab.architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.lang.ArchRule;
import jakarta.persistence.Entity;
import org.springframework.web.bind.annotation.RestController;

public final class ArchitectureRules {

    public static final ArchRule DOMAIN_IS_PURE = noClasses()
            .that().resideInAPackage("..domain..")
            .and().doNotHaveSimpleName("package-info")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "org.springframework..", "jakarta.persistence..", "com.fasterxml..",
                    "..application..", "..adapter..")
            .as("DOMAIN_IS_PURE")
            .allowEmptyShould(true);

    public static final ArchRule APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER = noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat().resideInAPackage("..adapter..")
            .as("APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER")
            .allowEmptyShould(true);

    public static final ArchRule ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER = classes()
            .that().areAnnotatedWith(Entity.class)
            .should().resideInAPackage("..adapter.out.persistence..")
            .as("ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER")
            .allowEmptyShould(true);

    public static final ArchRule CONTROLLERS_ONLY_IN_WEB_ADAPTER = classes()
            .that().areAnnotatedWith(RestController.class)
            .should().resideInAPackage("..adapter.in.web..")
            .as("CONTROLLERS_ONLY_IN_WEB_ADAPTER")
            .allowEmptyShould(true);

    private ArchitectureRules() {
    }
}
