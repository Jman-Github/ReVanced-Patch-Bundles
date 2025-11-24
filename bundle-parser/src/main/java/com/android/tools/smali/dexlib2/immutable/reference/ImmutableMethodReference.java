/*
 * This file is a copy of the upstream implementation from
 * https://github.com/google/smali (commit corresponding to 3.0.9),
 * included here so that we get the constructor overload introduced
 * after 3.0.5. The ReVanced patch bundle runtime still depends on
 * the older dexlib2 packaged inside revanced-patcher, so we ship
 * this version locally to satisfy patches compiled against the new
 * constructor.
 */

package com.android.tools.smali.dexlib2.immutable.reference;

import com.android.tools.smali.dexlib2.base.reference.BaseMethodReference;
import com.android.tools.smali.dexlib2.iface.reference.MethodReference;
import com.android.tools.smali.dexlib2.immutable.util.CharSequenceConverter;
import com.android.tools.smali.util.ImmutableUtils;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.util.List;

public class ImmutableMethodReference extends BaseMethodReference implements ImmutableReference {
    @Nonnull
    protected final String definingClass;
    @Nonnull
    protected final String name;
    @Nonnull
    protected final List<String> parameters;
    @Nonnull
    protected final String returnType;

    public ImmutableMethodReference(
        @Nonnull String definingClass,
        @Nonnull String name,
        @Nullable Iterable<? extends CharSequence> parameters,
        @Nonnull String returnType
    ) {
        this.definingClass = definingClass;
        this.name = name;
        this.parameters = CharSequenceConverter.immutableStringList(parameters);
        this.returnType = returnType;
    }

    public ImmutableMethodReference(
        @Nonnull String definingClass,
        @Nonnull String name,
        @Nullable List<String> parameters,
        @Nonnull String returnType
    ) {
        this.definingClass = definingClass;
        this.name = name;
        this.parameters = ImmutableUtils.nullToEmptyList(parameters);
        this.returnType = returnType;
    }

    @Nonnull
    public static ImmutableMethodReference of(@Nonnull MethodReference methodReference) {
        if (methodReference instanceof ImmutableMethodReference) {
            return (ImmutableMethodReference) methodReference;
        }
        return new ImmutableMethodReference(
            methodReference.getDefiningClass(),
            methodReference.getName(),
            methodReference.getParameterTypes(),
            methodReference.getReturnType()
        );
    }

    @Nonnull
    @Override
    public String getDefiningClass() {
        return definingClass;
    }

    @Nonnull
    @Override
    public String getName() {
        return name;
    }

    @Nonnull
    @Override
    public List<String> getParameterTypes() {
        return parameters;
    }

    @Nonnull
    @Override
    public String getReturnType() {
        return returnType;
    }
}
