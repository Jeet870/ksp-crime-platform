// Karnataka State Police Shield Logo (SVG)
export default function KSPLogo({ size = 64 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 110"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Shield shape */}
      <path
        d="M50 5 L90 20 L90 55 C90 78 70 95 50 105 C30 95 10 78 10 55 L10 20 Z"
        fill="#162d55"
        stroke="#c9a84c"
        strokeWidth="3"
      />
      {/* Inner shield border */}
      <path
        d="M50 12 L83 25 L83 55 C83 74 66 89 50 98 C34 89 17 74 17 55 L17 25 Z"
        fill="none"
        stroke="#c9a84c"
        strokeWidth="1.5"
        opacity="0.5"
      />
      {/* Star of India / Ashoka Chakra simplified */}
      <circle cx="50" cy="52" r="18" fill="none" stroke="#c9a84c" strokeWidth="1.5" opacity="0.8"/>
      {/* 8-pointed star */}
      <polygon
        points="50,34 53,46 65,46 56,53 59,65 50,58 41,65 44,53 35,46 47,46"
        fill="#c9a84c"
        opacity="0.9"
      />
      {/* KSP Text */}
      <text
        x="50"
        y="88"
        textAnchor="middle"
        fill="#c9a84c"
        fontSize="10"
        fontWeight="700"
        fontFamily="Space Grotesk, sans-serif"
        letterSpacing="2"
      >KSP</text>
      {/* Top banner */}
      <rect x="25" y="18" width="50" height="10" rx="2" fill="#c9a84c" opacity="0.15"/>
      <text
        x="50"
        y="26"
        textAnchor="middle"
        fill="#c9a84c"
        fontSize="5.5"
        fontWeight="600"
        fontFamily="Inter, sans-serif"
        letterSpacing="0.5"
      >KARNATAKA POLICE</text>
    </svg>
  );
}
