/*
	Installed from https://reactbits.dev/tailwind/
*/

const ShinyText = ({ text, disabled = false, speed = 2, className = "" }) => {
  const animationDuration = `${speed}s`;

  return (
    <div className="relative inline-block">
      {/* Base text - always visible */}
      <span className={`${className}`} style={{ color: '#DC2626' }}>
        {text}
      </span>
      
      {/* Shine overlay - only when not disabled */}
      {!disabled && (
        <span
          className={`absolute inset-0 bg-clip-text animate-shine ${className}`}
          style={{
            backgroundImage:
              "linear-gradient(120deg, rgba(255, 255, 255, 0) 40%, rgba(255, 255, 255, 0.8) 50%, rgba(255, 255, 255, 0) 60%)",
            backgroundSize: "200% 100%",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            animationDuration: animationDuration,
          }}
        >
          {text}
        </span>
      )}
    </div>
  );
};

export default ShinyText;

// tailwind.config.js
// module.exports = {
//   theme: {
//     extend: {
//       keyframes: {
//         shine: {
//           '0%': { 'background-position': '100%' },
//           '100%': { 'background-position': '-100%' },
//         },
//       },
//       animation: {
//         shine: 'shine 5s linear infinite',
//       },
//     },
//   },
//   plugins: [],
// };
