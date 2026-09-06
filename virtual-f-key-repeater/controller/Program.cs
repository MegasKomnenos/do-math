using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace VirtualFRepeater;

internal static class Program
{
    private const ushort VendorId = 0xCAFE;
    private const ushort ProductId = 0xF001;
    private const ushort DeviceVersion = 0x0102;
    private const ushort ControlUsagePage = 0xFF00;
    private const ushort ControlUsage = 0x0001;
    private const byte ControlReportId = 0x02;
    private const int VkF8 = 0x77;
    private const int VkF9 = 0x78;

    private static volatile bool _exitRequested;

    private static int Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;

        if (!TryParseArguments(args, out int intervalMs, out bool startEnabled, out bool probeOnly))
        {
            return 2;
        }

        using SafeFileHandle? device = FindControlDevice();
        if (device is null)
        {
            Console.Error.WriteLine("가상 F 키보드의 제어 장치를 찾지 못했습니다.");
            Console.Error.WriteLine("이번 빌드의 드라이버를 설치하거나 업데이트한 뒤 다시 실행하세요.");
            return 1;
        }

        Console.WriteLine("가상 F 키보드 연결: 성공");
        if (probeOnly)
        {
            return 0;
        }

        bool enabled = startEnabled;
        SendConfiguration(device, enabled, intervalMs);

        Console.CancelKeyPress += (_, eventArgs) =>
        {
            eventArgs.Cancel = true;
            _exitRequested = true;
        };

        Console.WriteLine("주기: F+B 200초 → F1 → 정지 500초 → F1 → 반복");
        Console.WriteLine($"F8: 새 주기 시작/정지 | F9: 종료 | 간격: {intervalMs}ms");
        Console.WriteLine(enabled ? "반복을 시작했습니다." : "F8을 누르면 반복을 시작합니다.");

        bool f8WasDown = false;
        bool f9WasDown = false;
        long lastHeartbeatAt = Environment.TickCount64;

        try
        {
            while (!_exitRequested)
            {
                bool f8IsDown = IsKeyDown(VkF8);
                bool f9IsDown = IsKeyDown(VkF9);

                if (f9IsDown && !f9WasDown)
                {
                    break;
                }

                if (f8IsDown && !f8WasDown)
                {
                    enabled = !enabled;
                    SendConfiguration(device, enabled, intervalMs);
                    lastHeartbeatAt = Environment.TickCount64;
                    Console.WriteLine(enabled
                        ? "반복을 시작했습니다."
                        : "주기를 정지했습니다. F8을 누르면 처음부터 시작합니다.");
                }

                f8WasDown = f8IsDown;
                f9WasDown = f9IsDown;

                if (enabled && Environment.TickCount64 - lastHeartbeatAt >= 500)
                {
                    SendConfiguration(device, true, intervalMs);
                    lastHeartbeatAt = Environment.TickCount64;
                }

                Thread.Sleep(5);
            }
        }
        finally
        {
            SendConfiguration(device, false, intervalMs);
        }

        Console.WriteLine("종료했습니다.");
        return 0;
    }

    private static bool TryParseArguments(
        string[] args,
        out int intervalMs,
        out bool startEnabled,
        out bool probeOnly)
    {
        intervalMs = 100;
        startEnabled = false;
        probeOnly = false;

        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--interval" when i + 1 < args.Length &&
                    int.TryParse(args[++i], out intervalMs) &&
                    intervalMs is >= 10 and <= 60000:
                    break;
                case "--start":
                    startEnabled = true;
                    break;
                case "--probe":
                    probeOnly = true;
                    break;
                default:
                    Console.Error.WriteLine(
                        "사용법: VirtualFRepeater [--interval 10..60000] [--start] [--probe]");
                    return false;
            }
        }

        return true;
    }

    private static void SendConfiguration(
        SafeFileHandle device,
        bool enabled,
        int intervalMs)
    {
        byte[] report =
        [
            ControlReportId,
            enabled ? (byte)1 : (byte)0,
            (byte)(intervalMs & 0xFF),
            (byte)((intervalMs >> 8) & 0xFF)
        ];

        if (!NativeMethods.HidD_SetFeature(device, report, report.Length))
        {
            throw new Win32Exception(
                Marshal.GetLastWin32Error(),
                "가상 키보드 설정을 전달하지 못했습니다.");
        }
    }

    private static SafeFileHandle? FindControlDevice()
    {
        NativeMethods.HidD_GetHidGuid(out Guid hidGuid);

        for (int attempt = 0; attempt < 3; attempt++)
        {
            int result = NativeMethods.CM_Get_Device_Interface_List_SizeW(
                out uint characterCount,
                ref hidGuid,
                null,
                NativeMethods.CmGetDeviceInterfaceListPresent);

            if (result != NativeMethods.CrSuccess || characterCount <= 1)
            {
                return null;
            }

            char[] paths = new char[characterCount];
            result = NativeMethods.CM_Get_Device_Interface_ListW(
                ref hidGuid,
                null,
                paths,
                characterCount,
                NativeMethods.CmGetDeviceInterfaceListPresent);

            if (result == NativeMethods.CrBufferSmall)
            {
                continue;
            }

            if (result != NativeMethods.CrSuccess)
            {
                throw new Win32Exception(result, "HID 장치 목록을 읽지 못했습니다.");
            }

            foreach (string path in ParseMultiString(paths))
            {
                SafeFileHandle handle = NativeMethods.CreateFileW(
                    path,
                    NativeMethods.GenericRead | NativeMethods.GenericWrite,
                    NativeMethods.FileShareRead | NativeMethods.FileShareWrite,
                    IntPtr.Zero,
                    NativeMethods.OpenExisting,
                    0,
                    IntPtr.Zero);

                if (handle.IsInvalid)
                {
                    handle.Dispose();
                    continue;
                }

                if (IsControlDevice(handle))
                {
                    return handle;
                }

                handle.Dispose();
            }

            return null;
        }

        return null;
    }

    private static bool IsControlDevice(SafeFileHandle handle)
    {
        var attributes = new NativeMethods.HiddAttributes
        {
            Size = Marshal.SizeOf<NativeMethods.HiddAttributes>()
        };

        if (!NativeMethods.HidD_GetAttributes(handle, ref attributes) ||
            attributes.VendorId != VendorId ||
            attributes.ProductId != ProductId ||
            attributes.VersionNumber != DeviceVersion)
        {
            return false;
        }

        if (!NativeMethods.HidD_GetPreparsedData(handle, out IntPtr preparsedData))
        {
            return false;
        }

        try
        {
            int status = NativeMethods.HidP_GetCaps(preparsedData, out NativeMethods.HidpCaps caps);
            return status >= 0 &&
                caps.UsagePage == ControlUsagePage &&
                caps.Usage == ControlUsage &&
                caps.FeatureReportByteLength == 4;
        }
        finally
        {
            NativeMethods.HidD_FreePreparsedData(preparsedData);
        }
    }

    private static IEnumerable<string> ParseMultiString(char[] value)
    {
        int start = 0;
        while (start < value.Length && value[start] != '\0')
        {
            int end = Array.IndexOf(value, '\0', start);
            if (end < 0)
            {
                yield break;
            }

            yield return new string(value, start, end - start);
            start = end + 1;
        }
    }

    private static bool IsKeyDown(int virtualKey) =>
        (NativeMethods.GetAsyncKeyState(virtualKey) & 0x8000) != 0;
}

internal static partial class NativeMethods
{
    internal const int CrSuccess = 0;
    internal const int CrBufferSmall = 26;
    internal const uint CmGetDeviceInterfaceListPresent = 0;
    internal const uint GenericRead = 0x80000000;
    internal const uint GenericWrite = 0x40000000;
    internal const uint FileShareRead = 0x00000001;
    internal const uint FileShareWrite = 0x00000002;
    internal const uint OpenExisting = 3;

    [StructLayout(LayoutKind.Sequential)]
    internal struct HiddAttributes
    {
        internal int Size;
        internal ushort VendorId;
        internal ushort ProductId;
        internal ushort VersionNumber;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct HidpCaps
    {
        internal ushort Usage;
        internal ushort UsagePage;
        internal ushort InputReportByteLength;
        internal ushort OutputReportByteLength;
        internal ushort FeatureReportByteLength;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 17)]
        internal ushort[] Reserved;

        internal ushort NumberLinkCollectionNodes;
        internal ushort NumberInputButtonCaps;
        internal ushort NumberInputValueCaps;
        internal ushort NumberInputDataIndices;
        internal ushort NumberOutputButtonCaps;
        internal ushort NumberOutputValueCaps;
        internal ushort NumberOutputDataIndices;
        internal ushort NumberFeatureButtonCaps;
        internal ushort NumberFeatureValueCaps;
        internal ushort NumberFeatureDataIndices;
    }

    [DllImport("hid.dll")]
    internal static extern void HidD_GetHidGuid(out Guid hidGuid);

    [DllImport("hid.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool HidD_GetAttributes(
        SafeFileHandle device,
        ref HiddAttributes attributes);

    [DllImport("hid.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool HidD_SetFeature(
        SafeFileHandle device,
        byte[] reportBuffer,
        int reportBufferLength);

    [DllImport("hid.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool HidD_GetPreparsedData(
        SafeFileHandle device,
        out IntPtr preparsedData);

    [DllImport("hid.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool HidD_FreePreparsedData(IntPtr preparsedData);

    [DllImport("hid.dll")]
    internal static extern int HidP_GetCaps(
        IntPtr preparsedData,
        out HidpCaps capabilities);

    [DllImport("cfgmgr32.dll", CharSet = CharSet.Unicode)]
    internal static extern int CM_Get_Device_Interface_List_SizeW(
        out uint length,
        ref Guid interfaceClassGuid,
        string? deviceId,
        uint flags);

    [DllImport("cfgmgr32.dll", CharSet = CharSet.Unicode)]
    internal static extern int CM_Get_Device_Interface_ListW(
        ref Guid interfaceClassGuid,
        string? deviceId,
        [Out] char[] buffer,
        uint bufferLength,
        uint flags);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    internal static extern SafeFileHandle CreateFileW(
        string fileName,
        uint desiredAccess,
        uint shareMode,
        IntPtr securityAttributes,
        uint creationDisposition,
        uint flagsAndAttributes,
        IntPtr templateFile);

    [DllImport("user32.dll")]
    internal static extern short GetAsyncKeyState(int virtualKey);
}
