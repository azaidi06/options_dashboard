/**
 * Input and Select components - dark theme
 */

export function Input({
  label,
  value,
  onChange,
  type = 'text',
  placeholder = '',
  className = '',
  disabled = false,
  ...props
}) {
  return (
    <div className={className}>
      {label && <label className="label">{label}</label>}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={`input ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        {...props}
      />
    </div>
  );
}

export function Select({
  label,
  value,
  onChange,
  options = [],
  className = '',
  disabled = false,
  ...props
}) {
  return (
    <div className={className}>
      {label && <label className="label">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`input ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        {...props}
      >
        {options.map((option) => (
          <option
            key={typeof option === 'object' ? option.value : option}
            value={typeof option === 'object' ? option.value : option}
          >
            {typeof option === 'object' ? option.label : option}
          </option>
        ))}
      </select>
    </div>
  );
}
