import { motion } from "motion/react";
import React from "react";


export const SharedLayoutBg = React.forwardRef<any, any>(
  ({ children, as = "div", className, pillClassName, pillContainerClassName, ...props }, ref) => {
    const Component = motion.create(as as any);
    return (
      <Component ref={ref} className={className} {...props}>
        {children}
      </Component>
    );
  }
);
