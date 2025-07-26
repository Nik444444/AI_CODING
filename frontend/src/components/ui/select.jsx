import React from "react";
import { cn } from "../../lib/utils";

const Select = ({ children, value, onValueChange, ...props }) => {
  return (
    <div className="relative">
      {React.Children.map(children, child => 
        React.cloneElement(child, { value, onValueChange, ...props })
      )}
    </div>
  );
};

const SelectTrigger = React.forwardRef(({ className, children, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
  >
    {children}
    <svg className="h-4 w-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  </button>
));
SelectTrigger.displayName = "SelectTrigger";

const SelectValue = ({ placeholder }) => (
  <span className="text-muted-foreground">{placeholder}</span>
);

const SelectContent = ({ className, children, ...props }) => (
  <div
    className={cn(
      "absolute top-full z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-80 zoom-in-95",
      className
    )}
    {...props}
  >
    {children}
  </div>
);

const SelectItem = ({ className, children, value, ...props }) => (
  <div
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue };