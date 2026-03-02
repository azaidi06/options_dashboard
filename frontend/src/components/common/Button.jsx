/**
 * Button component
 */
export function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  className = '',
  ...props
}) {
  const baseClass = variant === 'secondary' ? 'btn-secondary' : 'btn';
  const disabledClass = disabled ? 'opacity-50 cursor-not-allowed' : '';

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClass} ${disabledClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
