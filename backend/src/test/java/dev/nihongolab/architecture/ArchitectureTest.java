package dev.nihongolab.architecture;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

@AnalyzeClasses(packages = "dev.nihongolab",
        importOptions = ImportOption.DoNotIncludeTests.class )
class ArchitectureTest {

    @ArchTest static final ArchRule domainIsPure = ArchitectureRules.DOMAIN_IS_PURE;
    @ArchTest static final ArchRule applicationIndependent = ArchitectureRules.APPLICATION_DOES_NOT_DEPEND_ON_ADAPTER;
    @ArchTest static final ArchRule entities = ArchitectureRules.ENTITIES_ONLY_IN_PERSISTENCE_ADAPTER;
    @ArchTest static final ArchRule controllers = ArchitectureRules.CONTROLLERS_ONLY_IN_WEB_ADAPTER;
}
